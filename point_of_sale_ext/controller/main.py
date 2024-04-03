""" Import Package """
import logging
import json
import werkzeug.exceptions
from werkzeug.urls import url_parse
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools.misc import html_escape

from odoo.addons.web.controllers.report import ReportController

_logger = logging.getLogger(__name__)


class ReportController(ReportController):

    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, context=None, token=None):  # pylint: disable=unused-argument
        response = super().report_download(data=data, context=context, token=token)

        requestcontent = json.loads(data)
        url, type_ = requestcontent[0], requestcontent[1]
        reportname = '???'
        data_context = {}
        try:
            if type_ in ['qweb-pdf', 'qweb-text']:
                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')

                if not docids:
                    # Particular report:
                    data = url_parse(url).decode_query(cls=dict)  # decoding the args represented in JSON
                    if 'context' in data:
                        context, data_context = json.loads(context or '{}'), json.loads(data.pop('context'))

                if 'summary_report_name' in data_context:
                    filename = data_context['summary_report_name']

                else:
                    return response

                response.headers.remove('Content-Disposition')
                response.headers.add('Content-Disposition', content_disposition(filename))
                return response

        except Exception as e:
            _logger.exception("Error while generating report %s", reportname)
            se = http.serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            res = request.make_response(html_escape(json.dumps(error)))
            raise werkzeug.exceptions.InternalServerError(response=res) from e
        return response