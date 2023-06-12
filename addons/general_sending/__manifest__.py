# -*- coding: utf-8 -*-
{
    'name':         'Maknoon General Lib',
    'description':  "general libraries to use in Maknoon",
    'version':      '0.0.1',
    # "depends":      ["base", "bi_sms_client_generic","mk_student_register"],
    "depends":      ["base", "bi_sms_client_generic"],
    # "depends":      ["base"],

	"data":         [
					"views/gateway_config.xml",
                	"data/general_sending_data.xml",
                	"data/gateway_configuration.xml",
                	"data/gateway_parameters.xml",
		            ],
	'installable':  True,
	'auto_install': True,
	'application':  False,
}
