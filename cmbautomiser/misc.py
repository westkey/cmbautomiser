#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# bill_dialog.py
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

import subprocess, threading, os, posixpath, platform

from gi.repository import Gtk

## GLOBAL CONSTANTS

# Program name
PROGRAM_NAME = 'CMB Automiser'
# Item codes for data types
MEAS_NO = 1
MEAS_L = 2
MEAS_DESC = 3
MEAS_CUST = 4
# CMB error codes used for displaying info in main window
CMB_ERROR = -1
CMB_WARNING = -2
CMB_OK = 0
CMB_INFO = 0
# For tracking window management
CHILD_WINDOW = 1
PARENT_WINDOW = 0
main_hidden = 0
child_windows = 0
# Used in bill module for indicating type of bill
BILL_CUSTOM = 1
BILL_NORMAL = 2
# background colors for treeview
MEAS_COLOR_LOCKED = '#BABDB6'
MEAS_COLOR_NORMAL = '#FFFFFF'
MEAS_COLOR_SELECTED = '#729FCF'
# Timeout for killing Latex subprocess
LATEX_TIMEOUT = 300 # 5 minutes
# Item description wrap-width for screen purpose
CMB_DESCRIPTION_WIDTH = 60
CMB_DESCRIPTION_MAX_LENGTH = 1000
# Deviation statement
DEV_LIMIT_STATEMENT = 10
# List of units which will be considered as integer values
INT_ITEMS = ['point', 'points', 'pnt', 'pnts', 'number', 'numbers', 'no', 'nos', 'lot', 'lots',
             'lump', 'lumpsum', 'lump-sum', 'lump sum', 'ls', 'each','job','jobs','set','sets',
             'pair','pairs',
             'pnt.', 'no.', 'nos.', 'l.s.', 'l.s']
# String used for checking file version
PROJECT_FILE_VER = 'CMBAUTOMISER_FILE_REFERENCE_VER_3'
# Item codes for project global variables
global_vars = ['$cmbnameofwork$',
               '$cmbagency$',
               '$cmbagmntno$', 
               '$cmbsituation$',
               '$cmbdateofstart$',
               '$cmbdateofstartasperagmnt$',
               '$cmbissuedto$',
               '$cmbvarifyingauthority$',
               '$cmbvarifyingauthorityoffice$',
               '$cmbissuingauthority$',
               '$cmbissuingauthorityoffice$']
global_vars_captions = ['Name of Work', 
                        'Agency',
                        'Agreement Number',
                        'Situation',
                        'Date of Start',
                        'Date of start as per Agmnt.',
                        'CMB Issued to',
                        'Varifying Authority',
                        'Varifying Authority Office',
                        'Issuing Authority',
                        'Issuing Authority Office']
               
## GLOBAL VARIABLES

# Dict for storing saved settings
global_settings_dict = dict()

def set_global_platform_vars():
    """Setup global platform dependent variables"""
    
    if platform.system() == 'Linux':
        global_settings_dict['latex_path'] = 'pdflatex'
    elif platform.system() == 'Windows':
        global_settings_dict['latex_path'] = misc.abs_path(
                    'miketex\\miktex\\bin\\pdflatex.exe')

## GLOBAL CLASSES

class UserEntryDialog():
    """Creates a dialog box for entry of custom data fields
    
        Arguments:
            parent: Parent Window
            window_caption: Window Caption to be displayed on Dialog
            item_values: Item values to be requested from user
            item_captions: Description of item values to be shown to user
    """
    
    def __init__(self, parent, window_caption, item_values, item_captions):
        self.toplevel = parent
        self.entrys = []
        self.item_values = item_values
        self.item_captions = item_captions

        self.dialog_window = Gtk.Dialog(window_caption, parent, Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.dialog_window.set_title(window_caption)
        self.dialog_window.set_resizable(True)
        self.dialog_window.set_border_width(5)
        self.dialog_window.set_size_request(int(self.toplevel.get_size_request()[0]*0.8),-1)
        self.dialog_window.set_default_response(Gtk.ResponseType.OK)

        # Pack Dialog
        dialog_box = self.dialog_window.get_content_area()
        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)
        grid.set_border_width(5)
        grid.set_hexpand(True)
        dialog_box.add(grid)
        for caption in self.item_captions:
            # Captions
            user_label = Gtk.Label(caption)
            user_label.set_halign(Gtk.Align.END)
            # Text Entry
            user_entry = Gtk.Entry()
            user_entry.set_hexpand(True)
            user_entry.set_activates_default(True)
            # Pack Widgets
            grid.attach_next_to(user_label, None, Gtk.PositionType.BOTTOM, 1, 1)
            grid.attach_next_to(user_entry, user_label, Gtk.PositionType.RIGHT, 1, 1)
            self.entrys.append(user_entry)
        # Add data
        for value, user_entry in zip(self.item_values, self.entrys):
            user_entry.set_text(value)
                
    def run(self):
        """Display dialog box and modify Item Values in place
        
            Save modified values to "item_values" (item passed by reference)
            if responce is Ok. Discard modified values if response is Cancel.
            
            Returns:
                True on Ok
                False on Cancel
        """
        # Run dialog
        self.dialog_window.show_all()
        response = self.dialog_window.run()
        
        if response == Gtk.ResponseType.OK:
            # Get formated text and update item_values
            for key, user_entry in zip(range(len(self.item_values)), self.entrys):
                cell = user_entry.get_text()
                try:  # try evaluating string
                    if type(self.item_values[key]) is str:
                        cell_formated = str(cell)
                    elif type(self.item_values[key]) is int:
                        cell_formated = str(float(cell))
                    elif type(self.item_values[key]) is float:
                        cell_formated = str(int(cell))
                    else:
                        cell_formated = ''
                except:
                    cell_formated = ''
                self.item_values[key] = cell_formated
                
            self.dialog_window.destroy()
            return True
        else:
            self.dialog_window.destroy()
            return False


class ManageResourses:
    # Static Variables
    schedule_view = None
    measurements_view = None
    bills_view = None

    def __init__(self, schedule_view=None, measurements_view=None, bills_view=None):
        if schedule_view is not None:
            ManageResourses.schedule_view = schedule_view
            ManageResourses.measurements_view = measurements_view
            ManageResourses.bills_view = bills_view

    def update_bill_schedule_insert_item_at_row(self,itemlist,rows):
        if itemlist == None:
            itemlist = [[[100,100,0,[0],0,0]]*len(rows)]*len(self.bills_view.bills)
        for bill,item in zip(self.bills_view.bills,itemlist):
            for i in range(0, len(rows)):
                bill.data.item_part_percentage.insert(rows[i], item[i][0])
                bill.data.item_excess_part_percentage.insert(rows[i], item[i][1])
                bill.data.item_excess_rates.insert(rows[i], item[i][2])
                bill.data.item_qty.insert(rows[i], item[i][3])
                bill.data.item_normal_amount.insert(rows[i], item[i][4])
                bill.data.item_excess_amount.insert(rows[i], item[i][5])

    def update_bill_schedule_delete_row(self,rows):
        items_top = []
        rows.sort()
        for bill in self.bills_view.bills:
            items = []
            for i in range(0, len(rows)):
                d1 = bill.data.item_part_percentage[rows[i] - i]
                d2 = bill.data.item_excess_part_percentage[rows[i] - i]
                d3 = bill.data.item_excess_rates[rows[i] - i]
                d4 = bill.data.item_qty[rows[i] - i]
                d5 = bill.data.item_normal_amount[rows[i] - i]
                d6 = bill.data.item_excess_amount[rows[i] - i]
                # Add to items
                items = items + [[d1,d2,d3,d4,d5,d6]]
                # Delete elements
                del bill.data.item_part_percentage[rows[i] - i]
                del bill.data.item_excess_part_percentage[rows[i] - i]
                del bill.data.item_excess_rates[rows[i] - i]
                del bill.data.item_qty[rows[i] - i]
                del bill.data.item_normal_amount[rows[i] - i]
                del bill.data.item_excess_amount[rows[i] - i]
            items_top += [items]
        return items_top

    def update_billed_flags(self):
        # Update cmb measured flags. Also manages abstract in Measurements view

        from cmb import MeasurementsView, Measurement, MeasurementItemAbstract, MeasurementItemCustom, MeasurementItemHeading
        from bill import BillView

        if self.measurements_view is not None and self.bills_view is not None:
            # Reset all
            for count_cmb, cmb in enumerate(self.measurements_view.cmbs):  # unset all
                for count_meas, meas in enumerate(cmb):
                    if isinstance(meas, Measurement):
                        for count_meas_item, meas_item in enumerate(meas):
                            meas_item.set_billed_flag(False)

            # Set Billed Flag for all items carried over to abstractMeasurement
            for cmb in self.measurements_view.cmbs:
                for meas in cmb.items:
                    if isinstance(meas,Measurement):
                        for mitem in meas.items:
                            if isinstance(mitem,MeasurementItemAbstract):
                                for item in mitem.m_items:
                                    try:
                                        self.measurements_view.cmbs[item[0]][item[1]][item[2]].set_billed_flag(True)
                                    except:
                                        print(('Error found in meas-abstract: Item No.' + str(item) + '. Item Removed'))
                                        mitem.m_items.remove(item)

            # Set Billed flag for all items included in bill
            for bill in self.bills_view.bills:
                for item in bill.data.mitems:  # set flags from bill
                    try:
                        self.measurements_view.cmbs[item[0]][item[1]][item[2]].set_billed_flag(True)
                    except:
                        print(('Error found in ' + str(item) + ' in bill ' + bill.data.title + '. Item Removed'))
                        bill.data.mitems.remove(item)

## GLOBAL METHODS

def posix_path(*args):
    if platform.system() == 'Linux': 
        if len(args) > 1:
            return posixpath.join(*args)
        else:
            return args[0]
    elif platform.system() == 'Windows':
        if len(args) > 1:
            path = os.path.normpath(posixpath.join(*args))
        else:
            path = os.path.normpath(args[0])
        # remove any leading slash
        if path[0] == '\\':
            return path[1:]
        else:
            return path

def abs_path(*args):
    return os.path.join(os.path.split(__file__)[0],*args)

def run_latex(folder, filename):  # runs latex two passes
    if filename is not None:
        latex_exec = Command([globalvars.global_settings_dict['latex_path'], '-interaction=batchmode', '-output-directory=' + folder, filename])
        code = latex_exec.run(timeout=LATEX_TIMEOUT)
        if code == 0:
            code = latex_exec.run(timeout=LATEX_TIMEOUT)
            if code != 0:
                return CMB_ERROR
        else:
            return CMB_ERROR
    return CMB_OK

def replace_all(text, dic):
    for i, j in dic.items():
        j = clean_latex(j)
        text = text.replace(i, j)
    return text

def replace_all_vanilla(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def clean_markup(text):
    for splchar, replspelchar in zip(['&', '<', '>', ], ['&amp;', '&lt;', '&gt;']):
        text = text.replace(splchar, replspelchar)
    return text

def clean_latex(text):
    for splchar, replspelchar in zip(['\\', '#', '$', '%', '^', '&', '_', '{', '}', '~', '\n'],
                                     ['\\textbackslash ', '\# ', '\$ ', '\% ', '\\textasciicircum ', '\& ', '\_ ',
                                      '\{ ', '\} ', '\\textasciitilde ', '\\newline ']):
        text = text.replace(splchar, replspelchar)
    return text

# For running command in seperate thread
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd)
            self.process.communicate()
        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print('Terminating process')
            self.process.terminate()
            thread.join()
            return -1
        return 0
