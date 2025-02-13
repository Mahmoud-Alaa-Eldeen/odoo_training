# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import json
from datetime import datetime
import datetime as delta
import datetime as time
import pytz
import requests
import logging
import dateutil
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    zk_emp_id = fields.Char(string = 'Attendance Machine No.')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('zk_emp_id', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)


class zk_attendance_tmp(models.Model):
    _name = 'hr.attendance.zk.temp'

    machine_id = fields.Many2one(comodel_name="hr.attendance.zk.machine", string="Attendance Machine", required=True)
    user_number = fields.Char(string="Machine User Id", index=True)
    user = fields.Many2one(comodel_name="hr.employee", compute="_compute_user", store=True)
    date = fields.Datetime(string="Date", index=True)
    local_date = fields.Datetime(string='Date', compute="_compute_local_date", store=True,
                                 help='for display only as the datetime of the system is showing as 2 hours after')
    date_temp = fields.Date(string="Date Temp", index=True, compute="_compute_date", store=True)
    inoutmode = fields.Char(string="In/Out Mode")
    logged = fields.Boolean(string="Logged", default=False)
    reversed = fields.Boolean(string='Reversed', defult=True)

    @api.model
    def sudo_create_log(self, args):
        # create record if not found
        cr = self._cr
        cr.execute("""
                            select * from hr_attendance_zk_temp where date='{}' and inoutmode='{}'
                            and user_number='{}' and  machine_id='{}';
                            """.format(args['date'],
                                       args['inoutmode'], args['user_number'],
                                       args['machine_id']
                                       ))
        found = True if len(cr.dictfetchall()) > 0 else False

        if not found:
            self.env['hr.attendance.zk.temp'].sudo().create(args)
        return True

    @api.depends('user_number')
    def _compute_user(self):
        for rec in self:
            if rec.user_number:
                emps = self.env['hr.employee'].search([])
                for emp in emps:
                    if emp.zk_emp_id == rec.user_number:
                        rec.user = emp.id

    @api.depends('date')
    def _compute_date(self):
        for rec in self:
            if rec.date:
                egypt_timezone = datetime.strptime(str(rec.date), "%Y-%m-%d %H:%M:%S") + time.timedelta(hours=2)
                rec.date_temp = egypt_timezone.date()

    @api.depends('date')
    def _compute_local_date(self):
        for record in self:
            if record.date:
                record.local_date = datetime.strptime(str(record.date), "%Y-%m-%d %H:%M:%S") + time.timedelta(hours=2)


    @api.model
    def process_data(self):
        # Process_data
        today_date = str((datetime.today() + time.timedelta(hours=2)).date())
        not_pulled_today = self.env['hr.attendance.zk.machine'].search(
            [('last_download_log', '<', today_date + ' 00:00:00')])

        # if not_pulled_today:
        #     raise ValidationError(_('Machines must be downloaded first!'))

        conf = self.env['zk.attendance.setting'].get_values()
        today_date_val = str(time.date.today())
        records = self.search([('logged', '=', False),
                               ('date_temp', '!=', today_date_val)])
        date_in = None
        date_out = None
        employees = list(set(self.search([('logged', '=', False), ('user', "!=", False),
                                          ('date_temp', '!=', today_date_val)]).mapped('user_number')))
        for emp in employees:
            emp_obj = self.env['hr.employee'].search([('zk_emp_id', '=', emp)])
            if not emp_obj:
                continue
            datetime_list = records.filtered(lambda x: x.user_number == emp).mapped('date')
            dates = [x.date().strftime("%Y-%m-%d") for x in datetime_list]
            dates_unique = list(set(dates))
            for date in dates_unique:
                attendance_per_emp = records.filtered(
                    lambda x: x.user_number == emp and str(x.date_temp) == date).sorted()

                date_ins = attendance_per_emp

                if len(attendance_per_emp) < 1:
                    pass
                # in case of one check in a day,
                # create atrendance record with check in=check out
                elif date_ins:
                    date_out = max(date_ins.mapped('date'))
                    date_in = min(date_ins.mapped('date'))
                    local_check_in = date_in + time.timedelta(hours=2)
                    local_check_out = date_out + time.timedelta(hours=2)

                    self.env['hr.attendance'].create(
                        {'employee_id': emp_obj.id, 'check_in': date_in,
                         'local_check_in': local_check_in,
                         'local_check_out': local_check_out,
                         'check_out': date_out,
                         'missing_check': True if (local_check_in == local_check_out) else False,
                         })
                    attendance_per_emp.write({'logged': True})
                    self.env.cr.commit()


class zk_attendance_machine(models.Model):
    _name = "hr.attendance.zk.machine"

    machine_number = fields.Integer(string="Machine Number", default=0, readonly=True)
    name = fields.Char(string="Name")
    ip = fields.Char(string="IP", required=True)
    port = fields.Integer(string="port", default=4370)
    sync = fields.Boolean(string="Synced", default=False)
    model = fields.Char(string="Model")
    date_sync = fields.Datetime(string="Sync Date")
    date_sync_success = fields.Datetime(string="Successful Sync Date")
    manual_upload_sync_date = fields.Datetime(string="Last Manual Upload Date")
    sync_error = fields.Text(string="Sync Error")
    last_download_log = fields.Datetime('Last Download Log')

    ##
    @api.model
    def get_machine_last_download(self, args=None):
        self=self.sudo()
        if args['machine_id']:
            last_download_log= str(self.env['hr.attendance.zk.machine'].sudo().search(
                [('id', '=', int(args['machine_id']))]).last_download_log)

            #subtract 30 days from last download log, for any missing data for last 30 days
            #to be pulled in odoo again, and by itself reqpition in log is not permitted
            last_download_log=datetime.strptime(last_download_log, "%Y-%m-%d %H:%M:%S")- delta.timedelta(30)
            return str(last_download_log)

    @api.model
    def update_machine_last_download(self, args=None):  # machine_id, last_download
        # return self.sudo().do_update_machine_last_download(machine_id, last_download)
        if args is None:
            args = {}
        return self.sudo().do_update_machine_last_download(args['machine_id'], args['last_datetime'])

    @api.model
    def do_update_machine_last_download(self, machine_id, last_download):
        # if found:
        #as sure save all data for all machines once,update last donwload for all machines
        found = self.env['hr.attendance.zk.machine'].search([])
        if found:
            for rec in found:
                rec.write({
                    'last_download_log': last_download
                })
        return True


    @api.model
    def create(self, values):
        res = super(zk_attendance_machine, self).create(values)
        res['machine_number'] = res.id
        return res




    def process(self):
        # if there is ay machine not pulled today "process will run if all machines pulled" only
        today_date = str((datetime.today() + time.timedelta(hours=2)).date())

        # responsile to call process_data function from schedualed action
        self.env['hr.attendance.zk.temp'].process_data()


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    no_checkout = fields.Boolean(string="Missing Check-out", default=False)
    missing_check = fields.Boolean(string="Missing Check", default=False)

    no_check_in = fields.Boolean(string="Missing Check-in", default=False)

    local_check_in = fields.Datetime(string="Local Check In")
    local_check_out = fields.Datetime(string="Local Check Out")
