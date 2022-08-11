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
    "kubernetes": {
        'type': 'dict', 'valuesrules': {'type': 'dict'}
    },
    "ansible": {
        'type': 'list', 'schema': { 'type': 'dict', 'schema': {
                'hosts': {'type': 'string'},
                'name': {'type': 'string'}, 
                'roles': {
                    'type': 'list', 'schema': {'type': 'dict'}
                },
                'sudo_prompt': {'type': 'boolean'},
                'type': {'type': 'string'},
                'params': {'type': 'dict'},
                'source': {'type': 'string'}
            }
        }
    },
    "use_tf_backend": {
        'type': 'boolean'
    }
}
