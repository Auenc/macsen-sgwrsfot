#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import jsonpickle

import importlib

from nlp.cy.nlp import NaturalLanguageProcessing


class Brain(object):


    def __init__(self):
        self.skills = dict()
        self.nlp = NaturalLanguageProcessing()

        skills_root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'skills')
        
        self.load_skill(skills_root_dir, 'tywydd')
        self.load_skill(skills_root_dir, 'newyddion')


    def load_skill(self, skills_root_dir, skillname):
        skill_python_module = importlib.import_module('skills.%s.%s' % (skillname, skillname))
        class_ = getattr(skill_python_module, skillname + '_skill')
        instance = class_(skills_root_dir, skillname, self.nlp)
        self.skills[skillname] = instance

   
    def handle(self, text, latitude=0.0, longitude=0.0):
        # Bangor, Gwynedd 
        if latitude==0.0 and longitude==0.0:
            latitude=53.2167738950777
            longitude=-4.14310073720948

        handler_key, intent = self.determine_intent(text)
        skill_result=self.handle_intent(handler_key, intent, latitude, longitude)
        
        return intent.name, skill_result


    def handle_intent(self, handler_key, intent, latitude, longitude):
        return self.skills[handler_key].handle(intent, latitude, longitude)


    def determine_intent(self, text):
        best_intent = None
        best_handler = None

        for key in self.skills.keys():
            intent = self.skills[key].calculate_intent(text)
            if not best_intent:
                 best_intent = intent
                 best_handler = key
            if intent.conf > best_intent.conf:
                 best_intent = intent
                 best_handler = key
        return best_handler, best_intent 


    def expand_intents(self, include_additional_entities=False):
        result = []
        for name in self.skills.keys():
            skill = self.skills.get(name)
            result = result + skill.expand_intents(include_additional_entities)
        return result


if __name__ == "__main__":

    brain = Brain()
    #print('\n'.join(brain.expand_intents()))

    response = brain.handle(sys.argv[1])
    print (jsonpickle.encode(response))

