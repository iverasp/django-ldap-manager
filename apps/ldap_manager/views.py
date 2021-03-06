from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from models import LdapGroup, LdapUser, LdapOrgUnit
from forms import *
from lineage.settings import DEFAULT_HOME, DEFAULT_EMAIL
from string import Template
from django_tables2 import RequestConfig
from tables import UsersTable, GroupsTable

@login_required
@user_passes_test(lambda u: u.is_staff())
def initial(request):

    if not LdapOrgUnit.objects.filter(name="groups"):
        groups = LdapOrgUnit(name="groups")
        groups.save()
        print "made node groups"

    if not LdapOrgUnit.objects.filter(name="people"):
        print "yolo"
        groups = LdapOrgUnit(name="people")
        groups.save()
        print "made node people"

    return render(request, "initial.html")

def index(request):
    return render(request, 'index.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def users(request):
    table = UsersTable(LdapUser.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'users.html', {'table':table})

@login_required
@user_passes_test(lambda u: u.is_staff)
def user(request, username):
    user = LdapUser.objects.filter(username=username).first()
    if not user:
        return redirect('users')
    #print 'photo', user.photo
    form = UserForm(
        instance=user,
        initial= {
            'group': LdapGroup.objects.filter(
                gid=unicode(user.group)
            ).first(),
            'groups': LdapGroup.objects.filter(
                usernames__contains=unicode(user.username)
            ).all(),
            'enable_samba': False,
            'auto_uid': True,
            'auto_home': user.home_directory == make_home_path(user),
            'auto_email': user.email == make_email_adress(user),
        }
    )
    update_password_form = UpdatePasswordForm()
    if request.method == 'POST':
        form = UserForm(data=request.POST, instance=user)
        if not form.is_valid():
            print form.data
            print form.errors
        if form.is_valid():
            print "valid!"
            user = form.save(commit=False)
            user.save()
            return redirect('user', user.username)
    context = {
        'user': user,
        'form': form,
        'update_password_form': update_password_form,
    }
    return render(request, 'user.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def change_password(request, uid):
    if request.method == 'POST':
        form = UpdatePasswordForm(data=request.POST)
        if form.is_valid():
            user = LdapUser.objects.filter(uid=uid).first()
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            return redirect('user', user.uid)
    else:
        return redirect('user', uid)

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_user(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(data=request.POST)
        print form.data
        if not form.is_valid():
            print form.errors
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect('user', user.uid)
    context = {
        'form': form,
    }
    return render(request, 'user.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def groups(request):
    table = GroupsTable(LdapGroup.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'groups.html', {'table': table})

@login_required
@user_passes_test(lambda u: u.is_staff)
def group(request, name):
    group = LdapGroup.objects.filter(name=name).first()
    if not group:
        return redirect('groups')
    form = GroupForm(
        instance=group,
        initial= {
            'auto_gid': True,
        }
    )
    if request.method == 'POST':
        form = GroupForm(data=request.POST, instance=group)
        if not form.is_valid():
            print form.data
            print form.errors
        if form.is_valid():
            print "valid!"
            form.save()
            return redirect('group', group.gid)
    context = {
        'group': group,
        'form': form,
    }
    return render(request, 'group.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_group(request):
    form = GroupForm()
    if request.method == 'POST':
        form = GroupForm(data=request.POST)
        if not form.is_valid():
            print form.errors
        if form.is_valid():
            print "valid!"
            group = form.save(commit=False)
            group.save()
            return redirect('group', group.gid)
    context = {
        'form': form,
    }
    return render(request, 'group.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def sudoers(request):
    pass

@login_required
@user_passes_test(lambda u: u.is_staff)
def settings(request):
    form = SettingsForm()
    context = {
        'form': form,
    }
    return render(request, 'settings.html', context)

def make_home_path(user):
    return DEFAULT_HOME.safe_substitute(username=user.username)

def make_email_adress(user):
    return DEFAULT_EMAIL.safe_substitute(username=user.username)
