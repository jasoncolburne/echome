import logging
from django.shortcuts import render
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import viewsets, status
from api.api_view import HelperView
from identity.models import User
from .instance_definitions import InstanceDefinition, InvalidInstanceType
from .models import UserKey, VirtualMachine
from .serializers import VirtualMachineSerializer
from .vm_manager import *

logger = logging.getLogger(__name__)

####################
# Namespace: vm 
# vm/
# /vm/create
# Example command:
# curl <URL>/v1/vm/create\?ImageId=gmi-fc1c9a62 \
# \&InstanceSize=standard.small \
# \&NetworkInterfacePrivateIp=172.16.9.10\/24 \
# \&NetworkInterfaceGatewayIp=172.16.9.1 \
# \&KeyName=echome
class CreateVM(HelperView, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"got": True})

    def post(self, request):
        req_params = [
            "ImageId", 
            "InstanceType", 
            "NetworkProfile",
        ]
        logger.debug(request)
        if self.require_parameters(request, req_params):
            return self.missing_parameter_response()

        try:
            instance_class_size = request.POST["InstanceType"].split(".")
            instanceDefinition = InstanceDefinition(instance_class_size[0], instance_class_size[1])
        except Exception as e:
            logger.debug(e)
            return self.error_response(
                "Provided InstanceSize is not a valid type or size.",
                status.HTTP_400_BAD_REQUEST
            )
        
        tags = self.unpack_tags(request)

        disk_size = request.POST["DiskSize"] if "DiskSize" in request.POST else "10G"
        
        vm = VmManager()

        try:
            vm_id = vm.create_vm(
                user=request.user, 
                instanceType=instanceDefinition, 
                Tags=tags,
                KeyName=request.POST["KeyName"] if "KeyName" in request.POST else None,
                NetworkProfile=request.POST["NetworkProfile"],
                PrivateIp=request.POST["PrivateIp"] if "PrivateIp" in request.POST else "",
                ImageId=request.POST["ImageId"],
                DiskSize=disk_size    
            )
        except InvalidLaunchConfiguration as e:
            logger.debug(e)
            return self.error_response(
                "InvalidLaunchConfiguration: A supplied value was invalid and could not successfully build the virtual machine.",
                status = status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            logger.debug(e)
            return self.error_response(
                "ValueError: A supplied value was invalid and could not successfully build the virtual machine.",
                status = status.HTTP_400_BAD_REQUEST
            )
        except LaunchError as e:
            logger.exception(e)
            return self.error_response(
                "There was an error when creating the instance.",
                status = status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception(e)
            return self.internal_server_error_response()
                
        return self.success_response({"virtual_machine_id": vm_id})

class DescribeVM(HelperView, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vm_id:str):
        i = []

        try:
            if vm_id == "all":
                vms = VirtualMachine.objects.filter(
                    account=request.user.account
                )
            else:
                vms = []
                vms.append(VirtualMachine.objects.get(
                    account=request.user.account,
                    instance_id=vm_id
                ))
            
            for vm in vms:
                j_obj = VirtualMachineSerializer(vm).data
                state, state_int, _  = VmManager().get_vm_state(vm.instance_id)
                j_obj["state"] = {
                    "code": state_int,
                    "state": state,
                }
                i.append(j_obj)
        except VirtualMachine.DoesNotExist as e:
            logger.debug(e)
            return self.not_found_response()
        except Exception as e:
            return self.internal_server_error_response()

        return Response(i)

class TerminateVM(HelperView, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"got": True})

    def post(self, request, vm_id:str):
        try:
            VmManager().terminate_instance(vm_id, request.user)
        except VirtualMachineDoesNotExist:
            return self.not_found_response()
        except Exception:
            return self.internal_server_error_response()
        
        return self.success_response()

class ModifyVM(HelperView, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"got": True})

    def post(self, request, vm_id:str):
        req_params = [
            "Action",
        ]
        if self.require_parameters(request, req_params):
            return self.missing_parameter_response()

        action = request.POST['Action']

        if action == 'stop':
            try:
                VmManager().stop_instance(vm_id)
            except VirtualMachineDoesNotExist:
                return self.not_found_response()
            except Exception:
                return self.internal_server_error_response()
        
            return self.success_response()
        elif action == 'start':
            try:
                VmManager().start_instance(vm_id)
            except VirtualMachineDoesNotExist:
                return self.not_found_response()
            except VirtualMachineConfigurationException:
                return self.error_response(
                    "Could not start VM due to configuration issue. See logs for more details.",
                    status = status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception:
                return self.internal_server_error_response()
        
            return self.success_response()
        