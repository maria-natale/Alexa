# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import gettext

from ask_sdk_core.skill_builder import SkillBuilder, CustomSkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractRequestInterceptor, AbstractExceptionHandler)
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_model.services import ServiceException
from ask_sdk_model.services.reminder_management import Trigger, TriggerType, AlertInfo, SpokenInfo, SpokenText, \
    PushNotification, PushNotificationStatus, ReminderRequest

from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard
from ask_sdk_model import Response
from alexa import data
from utils import Device
from utils import extract_devices
import requests
import os
import pickle
import pytz
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
REQUIRED_PERMISSIONS = ["alexa::alerts:reminders:skill:readwrite"]
TIME_ZONE_ID = 'Europe/Rome'

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        
        speak_output = _(data.WELCOME_MESSAGE)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class RetrieveDevicesIntentHandler(AbstractRequestHandler):
    """Handler for Retrieve Devices Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RetrieveDevicesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        session_attr = handler_input.attributes_manager.session_attributes
        speak_output = ""

        r=requests.get("http://localhost:8080/RetrieveDevices/RetrieveDevicesServlet")
        if r.status_code==200:
            devices=extract_devices(r)

            if devices is None:
                speak_output+=_(data.SERVER_ERR)+"\n"
            else:
                if len(devices)>0:
                    if len(devices)==1:
                        speak_output+=_(data.ONE_DEVICE)+"\n"
                    else:
                        speak_output+=_(data.NUMBER_DEV_MSG).format(len(devices))+"\n"
                        if len(devices)>3:
                            speak_output+=_(data.FIRST_DEVICES)+"\n"
                    for i, device in enumerate(devices):
                        if i<3:
                            speak_output+= _(data.DEVICE_MSG).format(i+1,device.hostname, device.address)
                            speak_output+='<break time="1s"/> '
                else:
                    speak_output=_(data.NO_DEVICES_MSG)
        else:
            speak_output=_(data.NETWORK_ERR)
         
        devicesList=[]
        if devices is None:
            devicesList=None
        else:
            for device in devices:
                devicesList.append(device.__getstate__())
        session_attr["devices"]=devicesList

        if len(devices)>3:
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output) 
                .response
            )
        else:
            return (
                handler_input.response_builder
                .speak(speak_output)
                .response
            )
            

class AllDevicesIntentHandler(AbstractRequestHandler):
    """Handler for Retrieve Devices Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AllDevicesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        session_attr = handler_input.attributes_manager.session_attributes
        speak_output = ""

        if "devices" in session_attr:
            devicesList = session_attr["devices"]

            if devicesList is None:
                speak_output+=_(data.SERVER_ERR)+"\n"
            else:
                devices=[]
                for element in devicesList:
                    device=Device()
                    device.__setstate__(element)
                    devices.append(device)

                if len(devices)>0:
                    speak_output+= _(data.ALL_DEVICES)+"\n"
                    for i, device in enumerate(devices):
                        speak_output+= _(data.DEVICE_MSG).format(i+1,device.hostname, device.address)
                        speak_output+='<break time="1s"/> '

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )



class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.HELP_MSG)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )



class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.GOODBYE_MSG)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = _(data.REFLECTOR_MSG).format(intent_name)

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.ERROR)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        os.environ['LANGUAGE']=locale
        i18n = gettext.translation(
            'data', localedir='lambda/py/locales', languages=[locale], fallback=True)
        handler_input.attributes_manager.request_attributes["_"] = i18n.gettext

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


#sb = SkillBuilder()
sb = CustomSkillBuilder(api_client=DefaultApiClient())  # required to use remiders

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(RetrieveDevicesIntentHandler())
sb.add_request_handler(AllDevicesIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
# make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
