# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sky_project_id = fields.Many2one('project.project', string='Project', track_visibility='onchange')

    @api.multi
    def sky_project_create(self):
        self.ensure_one()
        if not self.analytic_account_id:
            raise ValidationError(_('Not found Analytic account'))
        project_id = self.env['account.analytic.account'].with_context(default_use_tasks=True).project_create(
            analytic_account_id=self.analytic_account_id.id, 
            vals={'name': self.name, 'use_tasks': True, 'type': 'contract'})
        if project_id:
            self.write({'sky_project_id': project_id})


    @api.multi
    def sky_view_tasks(self):
        return {
            "name": _('Project'),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "views": [[False, "kanban"], [False, "tree"], [False, "form"]],
            "domain": [["project_id", "=", self.sky_project_id and self.sky_project_id.id or False]],
        }