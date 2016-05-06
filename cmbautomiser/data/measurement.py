#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  measurement.py
#  
#  Copyright 2014 Manu Varkey <manuvarkey@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from gi.repository import Gtk, Gdk, GLib
from undo import undoable

import os.path, copy, logging

# local files import
import misc

# Setup logger object
log = logging.getLogger(__name__)

class Cmb:
	"""Stores a CMB data instance"""
    def __init__(self,name = ""):
        self.name = name
        self.items = []

    def append_item(self,item):
        item.set_cmb(self)
        self.items.append(item)
                
    def insert_item(self,index,item):
        item.set_cmb(self)
        self.items.insert(index,item)
        
    def remove_item(self,index):
        del(self.items[index])

    def __setitem__(self, index, value):
        self.items[index] = value
    
    def __getitem__(self, index):
        return self.items[index]
        
    def set_name(self,name):
        self.name = name
        
    def get_name(self):
        return self.name
        
    def length(self):
        return len(self.items)
        
	def get_model(self):
		model = ['CMB',[self.name]]
		items_model = []
		for item in self.items:
			items_model.append(item.get_model())
		model.append(items_model)
		return model
	
	def set_model(self, model):
		if model[0] == 'CMB':
			self.name = model[1][0]
			self.items = []
			for item_model in model[2]:
				if item_model[0] in ['Measurement','Completion']:
					item_type = globals()[item_model[0]]
					item = item_type()
					item.set_model(item_model)
					self.items.append(item)

    def clear(self):
        self.items = []
        
    def get_latex_buffer(self,path):
		latex_buffer = misc.LatexFile()
        cmb_local_vars = {}
        cmb_local_vars['$cmbbookno$'] = self.name
        cmb_local_vars['$cmbheading$'] = ' '
        cmb_local_vars['$cmbtitle$'] = 'DETAILS OF MEASUREMENTS'
        cmb_local_vars['$cmbstartingpage$'] = str(1)
        
        latex_buffer.add_preffix_from_file('../latex/preamble.tex')
        latex_buffer.replace_and_clean(cmb_local_vars)
        for count,item in enumerate(self.items):
            newpath = list(path) + [count]
            latex_buffer += item.get_latex_buffer(newpath)
        latex_buffer.add_suffix_from_file('../latex/end.tex')
        return latex_buffer
        
    def get_text(self):
        return "<b>CMB No." + misc.clean_markup(self.name) + "</b>"
    
    def get_tooltip(self):
        return None
    
    def print_item(self):
        print("CMB " + self.name)
        for item in self.items:
            item.print_item()
        
class Measurement:
	"""Stores a Measurement groups"""
    def __init__(self,date = ""):
        self.date = date
        self.items = []

    def append_item(self,item):
        item.set_measurement(self)
        self.items.append(item)
                
    def insert_item(self,index,item):
        item.set_measurement(self)
        self.items.insert(index,item)
        
    def remove_item(self,index):
        del(self.items[index])

    def __setitem__(self, index, value):
        self.items[index] = value
    
    def __getitem__(self, index):
        return self.items[index]
        
    def set_date(self,date):
        self.date = date
        
    def get_date(self):
        return self.date

    def length(self):
        return len(self.items)
	
	def get_model(self):
		model = ['Measurement',[self.date]]
		items_model = []
		for item in self.items:
			items_model.append(item.get_model())
		model.append(items_model)
		return model
	
	def set_model(self, model):
		if model[0] == 'Measurement':
			self.date = model[1][0]
			self.items = []
			class_list = ['MeasurementItemHeading',
						  'MeasurementItemCustom',
						  'MeasurementItemAbstract']
			for item_model in model[2]:
				if item_model[0] in class_list:
					item_type = globals()[item_model[0]]
					item = item_type()
					item.set_model(item_model)
					self.items.append(item)
        
	def get_latex_buffer(self,path):
        latex_buffer = misc.LatexFile()
        latex_buffer.add_preffix_from_file('../latex/measgroup.tex')
        # replace local variables
        measgroup_local_vars = {}
        measgroup_local_vars['$cmbmeasurementdate$'] = self.date
        latex_buffer.replace_and_clean(measgroup_local_vars)
        
        for count,item in enumerate(self.items):
            newpath = list(path) + [count]
            latex_buffer += item.get_latex_buffer(newpath)
        return latex_buffer
        
    def clear(self):
        self.items = []
    
    def get_text(self):
        return "<b>Measurement dated." + clean_markup(self.date) + "</b>"
    
    def get_tooltip(self):
        return None
    
    def print_item(self):
        print("  " + "Measurement dated " + self.date)
        for item in self.items:
            item.print_item()
        
class MeasurementItem:
	"""Base class for storing Measurement items"""
    def __init__(self, itemnos=[], records=[], remark="", item_remarks=[]):
        self.itemnos = itemnos
        self.records = records
        self.remark = remark
        self.item_remarks = item_remarks

    def set_item(self,index,itemno):
        self.itemnos[index] = itemno
        
    def get_item(self,index):
        return self.itemnos[index]
        
    def append_record(self,record):
        self.records.append(record)
                
    def insert_record(self,index,record):
        self.records.insert(index,record)
        
    def remove_record(self,index):
        del(self.records[index])
        
    def __setitem__(self, index, value):
        self.records[index] = value
    
    def __getitem__(self, index):
        return self.records[index]
        
    def set_remark(self,remark):
        self.remark = remark
        
    def get_remark(self):
        return self.remark

    def length(self):
        return len(self.records)
        
    def clear(self):
        self.itemnos = []
        self.records = []
        self.remark = ''
        self.item_remarks = []
                
class MeasurementItemHeading(MeasurementItem):
	"""Stores an item heading"""
    def __init__(self,remark):
        MeasurementItem.__init__(self,itemnos=[],records=[],remark=remark,item_remarks = None)
	
	def get_model(self):
		model = ['MeasurementItemHeading',[self.remark]]
		return model
	
	def set_model(self, model):
		if model[0] == 'MeasurementItemHeading':
			self.remark = model[1][0]
        
    def get_latex_buffer(self,path):
        latex_buffer = misc.LatexFile()
        latex_buffer.add_preffix_from_file('..latex/measheading.tex')        
        # replace local variables
        measheading_local_vars = {}
        measheading_local_vars['$cmbmeasurementheading$'] = self.remark
        latex_buffer.replace_and_clean(measheading_local_vars)
        return latex_buffer
    
    def get_text(self):
        return "<b><i>" + misc.clean_markup(self.remark) + "</i></b>"
    
    def get_tooltip(self):
        return None
        
	def print_item(self):
        print("    " + self.remark)

class RecordCustom:
	"""An individual record of a MeasurementItemCustom"""
    def __init__(self, items, cust_funcs, total_func, columntypes):
        self.data_string = items
        self.data = []
        # Populate Data
        for x,columntype in zip(self.data_string,columntypes):
            if columntype not in [MEAS_DESC,MEAS_CUST]:
                try:
                    num = eval(x)
                    self.data.append(num)
                except:
                    self.data.append(0)
            else:
                self.data.append(0)
        self.cust_funcs = cust_funcs
        self.total_func = total_func
        self.columntypes = columntypes
        self.total = self.find_total()

    def get(self):
		#TODO
        iter_d = 0
        skip = 0
        data = []
        for columntype in self.columntypes:
            if columntype == MEAS_CUST:
                data.append('')
                skip += 1
            else:
                data.append(self.data_string[iter_d-skip])
            iter_d += 1
        return data

    def get_model(self):
        return self.data_string
        
	def set_model(self, items, cust_funcs, total_func, columntypes):
        self.__init__(items, cust_funcs, total_func, columntypes)

    def find_total(self):
        return self.total_func(self.data)

    def find_custom(self,index):
        return self.cust_funcs[index](self.data)

    def print_item(self):
        print("      " + str([self.data_string,self.total]))


class MeasurementItemCustom(MeasurementItem):
	"""Stores a custom record set [As per plugin loaded]"""
    def __init__(self, data = None, plugin=None):
        self.name = ''
        self.itemtype = None
        self.itemnos_mask = []
        self.captions = []
        self.columntypes = []
        self.cust_funcs = []
        self.total_func_item = None
        self.total_func = None
        self.latex_item = ''
        self.latex_record = ''
        # For user data support
        self.captions_udata = []
        self.columntypes_udata = []
        self.user_data = None
        self.latex_postproc_func = None
        self.export_abstract = None

        # Read description from file
        if plugin is not None:
            try:
                package = __import__('../templates.' + plugin)
                module = getattr(package, plugin)
                self.custom_object = module.CustomItem()
                self.name = self.custom_object.name
                self.itemtype = plugin
                self.itemnos_mask = self.custom_object.itemnos_mask
                self.captions = self.custom_object.captions
                self.columntypes = self.custom_object.columntypes
                self.cust_funcs = self.custom_object.cust_funcs
                self.total_func_item = self.custom_object.total_func_item
                self.total_func = self.custom_object.total_func
                self.latex_item = self.custom_object.latex_item
                self.latex_record = self.custom_object.latex_record
                # For user data support
                self.captions_udata = self.custom_object.captions_udata
                self.columntypes_udata = self.custom_object.columntypes_udata
                self.latex_postproc_func = self.custom_object.latex_postproc_func
                self.user_data = self.custom_object.user_data_default
                self.export_abstract = self.custom_object.export_abstract
            except ImportError:
                log.error('Error Loading plugin - MeasurementItemCustom - ' + str(plugin))

            if data != None:
                itemnos = data[0]
                
                records = []
                for item_model in data[1]:
					item = RecordCustom(item_model, cust_funcs, total_func, 
                
                remark = data[2]
                item_remarks = data[3]
                self.user_data = data[4]
                MeasurementItem.__init__(self, itemnos, records, remark, item_remarks)
            else:
                MeasurementItem.__init__(self, [None]*self.item_width(), [],
										 '', ['']*self.item_width())
        else:
            MeasurementItem.__init__(self)

    def model_width(self):
        return len(self.columntypes)

    def item_width(self):
        return len(self.itemnos_mask)

    def get_model(self):
        item_schedule = []
        for item in self.records:
            item_schedule.append(item.get_model())
        data = [self.itemnos, item_schedule, self.remark, self.item_remarks,
                 self.user_data, self.itemtype]
        return ['MeasurementItemCustom', data]

    def set_model(self, data):
		if data[1] == 'MeasurementItemCustom':
			self.clear()
			self.__init__(data[1], data[5])

    def get_latex_buffer(self,path,isabstract=False):
        latex_records = misc.LatexFile()
        
        data_string = [None]*self.model_width()
        for slno,record in enumerate(self.records):
            meascustom_rec_vars = {}
            meascustom_rec_vars_van = {}
            # Evaluate string to make replacement
            cust_iter = 0
            for i,columntype in enumerate(self.columntypes): # evaluate string of data entries, suppress zero.
                if columntype == MEAS_CUST:
                    try:
                        value =  str(record.cust_funcs[cust_iter](record.get(),slno))
                        data_string[i] = value if value not in ['0','0.0'] else ''
                    except:
                        data_string[i] = ''
                    cust_iter += 1
                elif columntype == MEAS_DESC:
                    try:
                        data_string[i] = str(record.data_string[i-cust_iter])
                    except:
                        data_string[i] = ''
                else:
                    try:
                        data_string[i] = str(record.data[i-cust_iter]) if record.data[i-cust_iter] != 0 else ''
                    except:
                        data_string[i] = ''
                # Check for carry over item possibly contains code
                if columntype == MEAS_DESC and data_string[i].find('Qty B/F') != -1:
                    meascustom_rec_vars_van['$data' + str(i+1) + '$'] = data_string[i]
                else:
                    meascustom_rec_vars['$data' + str(i+1) + '$'] = data_string[i]
            meascustom_rec_vars['$slno$'] = str(slno+1)
            
            latex_record = misc.LatexFile(self.latex_record)
            latex_record.replace(meascustom_rec_vars_van)
            latex_record.replace_and_clean(meascustom_rec_vars)
            latex_records += latex_record
            
        # replace local variables
        meascustom_local_vars = {}
        meascustom_local_vars_vannilla = {}
        for i in range(0,self.item_width()):
            try:
                meascustom_local_vars['$cmbitemdesc' + str(i+1) + '$'] = str(self.items[i].extended_description)
                meascustom_local_vars['$cmbitemno' + str(i+1) + '$'] = str(self.itemnos[i])
                meascustom_local_vars['$cmbtotal' + str(i+1) + '$'] = str(self.get_total()[i])
                meascustom_local_vars['$cmbitemremark' + str(i+1) + '$'] = str(self.item_remarks[i])
                meascustom_local_vars['$cmbcarriedover' + str(i+1) + '$'] = 'ref:abs:'+str(path)+':'+str(i+1)
                meascustom_local_vars['$cmblabel' + str(i+1) + '$'] = 'ref:meas:'+str(path)+':'+str(i+1)
                meascustom_local_vars_vannilla['$cmbitemexist' + str(i+1) + '$'] = '\\iftrue'
            except:
                meascustom_local_vars['$cmbitemdesc' + str(i+1) + '$'] = ''
                meascustom_local_vars['$cmbitemno' + str(i+1) + '$'] = 'ERROR'
                meascustom_local_vars['$cmbtotal' + str(i+1) + '$'] = ''
                meascustom_local_vars['$cmbitemremark' + str(i+1) + '$'] = ''
                meascustom_local_vars_vannilla['$cmbitemexist' + str(i+1) + '$'] = '\\iffalse'
        meascustom_local_vars['$cmbremark$'] = str(self.remark)
        if isabstract:
            meascustom_local_vars_vannilla['$cmbasbstractitem$'] = '\\iftrue'
        else:
            meascustom_local_vars_vannilla['$cmbasbstractitem$'] = '\\iffalse'
	    # fill in records - vanilla used since latex_records contains latex code
        meascustom_local_vars_vannilla['$cmbrecords$'] = latex_records
            
        latex_buffer = misc.LatexFile(self.latex_item)
        latex_buffer.replace_and_clean(meascustom_local_vars)
        latex_buffer.replace(meascustom_local_vars_vannilla)
        
        latex_post = self.latex_postproc_func(self.records,self.user_data,latex_buffer,isabstract)
        return latex_post

    def print_item(self):
        print("    Item No." + str(self.itemnos))
        for i in range(self.length()):
            self[i].print_item()
        print("    " + "Total: " + str(self.get_total()))

    def get_total(self):
        if self.total_func is not None:
            return self.total_func(self.records,self.user_data)
        else:
            return []

    def get_text(self):
        total = ['{:.1f}'.format(x) for x in self.get_total()]
        return "Item No.<b>" + str(self.itemnos) + "    |Custom: " + self.name + "|</b>    # of records: <b>" + \
               str(self.length()) + "</b>, Total: <b>" + str(total) + "</b>"

    def get_tooltip(self):
        if self.remark != "":
            return "Remark: " + self.remark
        else:
            return None

# Abstract of measurement
class MeasurementItemAbstract(MeasurementItem):
    def __init__(self,data = None):
        self.int_m_item = None # used to store all records and stuff
        self.m_items = None

        if data is not None:
            self.set_model(data)
        MeasurementItem.__init__(self,itemnos=[],items=[],records=[],remark='',item_remarks = [])

    def get_model(self):
        model = None
        itemtype = None
        if self.int_m_item is not None:
            model = self.int_m_item.get_model()
            itemtype = self.int_m_item.itemtype
        data = [self.m_items,model,itemtype]
        return data

    def set_model(self,data):
        self.int_m_item = None # used to store all records and stuff
        self.m_items = None

        if data is not None:
            self.m_items = data[0]
            if self.m_items is not None:
                self.int_m_item = MeasurementItemCustom(None,data[2])
                self.int_m_item.set_model(data[1])
                MeasurementItem.__init__(self,self.int_m_item.itemnos,self.int_m_item.items,self.int_m_item.records,
                              self.int_m_item.remark,self.int_m_item.item_remarks)

    def get_latex_buffer(self,path):
        if self.m_items is not None:
            return self.int_m_item.get_latex_buffer(path,True)

    def print_item(self):
        print('    Abstract Item')
        self.int_m_item.print_item()

    def get_total(self):
        if self.int_m_item is not None:
            return self.int_m_item.get_total()
        else:
            return []

    def get_text(self):
        if self.int_m_item is not None:
            return 'Abs: ' + self.int_m_item.get_text()
        else:
            return 'Abs: NOT DEFINED'

    def get_tooltip(self):
        if self.int_m_item is not None:
            if self.int_m_item.get_tooltip() is not None:
                return 'Abs: ' + self.int_m_item.get_tooltip()

class Completion:
	"""Class storing Completion date"""
    def __init__(self,date = "",remark = ""):
        self.date = date

    def set_date(self,date):
        self.date = date

    def get_date(self):
        return self.date
        
	def get_model(self):
		model = ['Completion',[self.date]]
		return model
	
	def set_model(self, model):
		if model[0] == 'Completion':
			self.date = model[1][0]
	
	def get_latex_buffer(self,path):
		latex_buffer = misc.LatexFile()
        latex_buffer.add_preffix_from_file('../latex/meascompletion.tex')
        # replace local variables
        measgroup_local_vars = {}
        measgroup_local_vars['$cmbcompletiondate$'] = self.date
        latex_buffer.replace_and_clean(measgroup_local_vars)
        return latex_buffer

    def get_text(self):
        return "<b>Completion recorded on " + clean_markup(self.date) + "</b>"

    def get_tooltip(self):
        return None

    def print_item(self):
        print("  " + "Completion recorded on " + self.date)