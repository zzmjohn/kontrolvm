from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.hypervisor.models import Hypervisor
from apps.storagepool.models import StoragePool
from apps.instance.models import Instance
from apps.hypervisor.forms import HypervisorForm
from apps.shared.forms import SizeForm
from apps.shared.models import Size
from django.contrib import messages
import persistent_messages
import simplejson

def view(request, pk):
  if not request.user.is_staff: raise Http404

  instance = get_object_or_404(Hypervisor, pk=pk)

  storagepools = StoragePool.objects.filter(hypervisor=instance)
  total_storagepool_allocated = 0
  for i in storagepools: total_storagepool_allocated += i.allocated

  instances = Instance.objects.filter(volume__storagepool__hypervisor=instance)

  instances_online = 0
  instances_offline = 0
  for i in instances: 
    if i.status == 1: instances_online += 1 
    else: instances_offline += 1
  allocated_memory = 0
  allocated_vcpus = 0
  for i in instances:
    allocated_memory += i.memory.size
    allocated_vcpus += i.vcpu

  maximum_memory_form = SizeForm(prefix="memory")
  maximum_hdd_form = SizeForm(prefix="memory")

  size_array = []
  for i in Size.objects.all():
    size_array.append({'value': i.id, 'text': i.name})

  return render_to_response('hypervisor/view.html',
    {
    'instance': instance,
    'instances': instances,
    'instances_online': instances_online,
    'instances_offline': instances_offline,
    'storagepools': storagepools,
    'total_storagepool_allocated': total_storagepool_allocated,
    'allocated_memory': allocated_memory,
    'allocated_vcpus': allocated_vcpus,
    'maximum_memory_form': maximum_memory_form,
    'maximum_hdd_form': maximum_hdd_form,
    'size_array': simplejson.dumps(size_array),
    },
    context_instance=RequestContext(request))

def index(request):
  if not request.user.is_staff: raise Http404
  hypervisors = Hypervisor.objects.all()
  return render_to_response('hypervisor/index.html', {
      'hypervisors': hypervisors,
    },
    context_instance=RequestContext(request))

def add(request):
  if not request.user.is_staff: raise Http404
  form = HypervisorForm()
  
  if request.method == "POST":
    form = HypervisorForm(request.POST)
    if form.is_valid():
      (hypervisor, created) = Hypervisor.objects.get_or_create(
        name=form.cleaned_data['name'],
        location=form.cleaned_data['location'],
        address=form.cleaned_data['address'],
        timeout=form.cleaned_data['timeout'],
        libvirt_port=form.cleaned_data['libvirt_port'],
        node_port=form.cleaned_data['node_port'],
        install_medium_path=form.cleaned_data['install_medium_path'],
        maximum_memory=form.cleaned_data['maximum_memory'],
        maximum_vcpus=form.cleaned_data['maximum_vcpus'],
        maximum_hdd=form.cleaned_data['maximum_hdd'],
      )
      if created: hypervisor.save()
      return redirect('/hypervisor/')

  return render_to_response('hypervisor/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))

def edit(request):
  if not request.user.is_staff: raise Http404
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      hypervisor = Hypervisor.objects.get(pk=json['pk'])
      orig_name = hypervisor.name
      orig_value = None
      if json['name'] == 'name':
        orig_value = hypervisor.name
        hypervisor.name = json['value']
      elif json['name'] == 'status':
        orig_value = hypervisor.status
        hypervisor.status = json['value']
      elif json['name'] == 'location':
        orig_value = hypervisor.location
        hypervisor.location = json['value']
      elif json['name'] == 'address':
        orig_value = hypervisor.address
        hypervisor.address = json['value']
      elif json['name'] == 'libvirt_port':
        orig_value = hypervisor.libvirt_port
        hypervisor.libvirt_port = json['value']
      elif json['name'] == 'node_port':
        orig_value = hypervisor.node_port
        hypervisor.node_port = json['value']
      elif json['name'] == 'maximum_hdd':
        size = Size.objects.get(id=json['value'])
        orig_value = hypervisor.maximum_hdd
        hypervisor.maximum_hdd = size
      elif json['name'] == 'maximum_memory':
        size = Size.objects.get(id=json['value'])
        orig_value = hypervisor.maximum_memory
        hypervisor.maximum_memory = size
      elif json['name'] == 'maximum_vcpus':
        orig_value = hypervisor.maximum_vcpus
        hypervisor.maximum_vcpus = json['value']
      else:
        raise Http404
      hypervisor.save()
      messages.add_message(request, persistent_messages.SUCCESS, 
        'Changed Hypervisor %s %s from %s to %s' % (orig_name, json['name'], orig_value, json['value']))
    except Hypervisor.DoesNotExist:
      raise Http404
    return HttpResponse('{}', mimetype="application/json")
  raise Http404

def start(request, pk):
  if not request.user.is_staff: raise Http404
  hypervisor = get_object_or_404(Hypervisor, pk=pk)
  hypervisor.start()
  messages.add_message(request, persistent_messages.SUCCESS,
    'Started Hypervisor %s' % (hypervisor))
  return redirect('/hypervisor/')
  
def stop(request, pk):
  if not request.user.is_staff: raise Http404
  hypervisor = get_object_or_404(Hypervisor, pk=pk)
  hypervisor.stop()
  messages.add_message(request, persistent_messages.SUCCESS,
    'Stopped Hypervisor %s' % (hypervisor))
  return redirect('/hypervisor/')

def delete(request, pk):
  if not request.user.is_staff: raise Http404
  hypervisor = get_object_or_404(Hypervisor, pk=pk)
  hypervisor.delete()
  return redirect('/hypervisor/')

def update(request, pk):
  if not request.user.is_staff: raise Http404
  hypervisor = get_object_or_404(Hypervisor, pk=pk)
  conn = hypervisor.get_connection(True)
  return redirect('/hypervisor/')
