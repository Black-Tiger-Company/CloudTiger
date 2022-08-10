{
    "network": {
        'type': 'dict', 'valuesrules': {'type': 'dict'}
    },
    "vm": {
        'type': 'dict', 'valuesrules': {'type': 'dict'}
    },
    "provider": {
        'type': 'string'
    },
    "ansible": {
        'type': 'list', 'schema': { 'type': 'dict', 'schema': {
                'hosts': {'type': 'string'},
                'name': {'type': 'string'}, 
                'roles': {
                    'type': 'list', 'schema': {'type': 'dict'}
                },
                'sudo_prompt': {'type': 'boolean'},
                'type': {'type': 'string'}
            }
        }
    }
}
