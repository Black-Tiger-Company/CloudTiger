"""
This file stores the expected outputs for CLI tests
"""

expected_outputs = {
    "init_0" : {
        "aws/single_scope" : 'Starting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\ninit action on scope aws/single_scope\nThe private SSH key ./secrets/ssh/id_rsa does exist, going forward\nFinished init action sucessfully\n'
    },
    "init_1" : {
        "aws/single_scope" : 'Starting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\ninit action on scope aws/single_scope\nFinished init action sucessfully\n'
    },
    "init_2" : {
        "aws/single_scope" : 'Starting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\ninit action on scope aws/single_scope\nFinished init action sucessfully\nStarting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\ninit action on scope aws/single_scope\nCreating scope folder PROJECT_ROOT/scopes/aws/single_scope\nSuccessfully created and set scope folder\nFinished init action sucessfully\n'
    },
    "missing_init_ip" : {
        "aws/single_scope" : 'Starting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\ninit action on scope aws/single_scope\nCreating scope folder PROJECT_ROOT/scopes/aws/single_scope\nMissing config_ips.yml file, please run cloudtiger <SCOPE> init 1\n'
    },
    "tf_init" : {
        "aws/single_scope" : 'Starting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\ninit action on scope aws/single_scope\nFinished init action sucessfully\nStarting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\ninit action on scope aws/single_scope\nCreating scope folder PROJECT_ROOT/scopes/aws/single_scope\nSuccessfully created and set scope folder\nFinished init action sucessfully\nStarting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\nExecuting Terraform command init\nBash action : terraform init --var-file=services/kubernetes.tfvars --var-file=services/network.tfvars --var-file=services/policy.tfvars --var-file=services/profile.tfvars --var-file=services/role.tfvars --var-file=services/vm.tfvars\nExecution of command :\nterraform init --var-file=services/kubernetes.tfvars --var-file=services/network.tfvars --var-file=services/policy.tfvars --var-file=services/profile.tfvars --var-file=services/role.tfvars --var-file=services/vm.tfvars > cloudtiger_std.log \nin folder PROJECT_ROOT/scopes/aws/single_scope/terraform\n\nBash action terminated\nFinished tf action sucessfully\n'
    },
    "tf_plan" : {
        "aws/single_scope" : 'Starting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\nExecuting Terraform command plan\nBash action : terraform plan --var-file=services/kubernetes.tfvars --var-file=services/network.tfvars --var-file=services/policy.tfvars --var-file=services/profile.tfvars --var-file=services/role.tfvars --var-file=services/vm.tfvars -json\nExecution of command :\nterraform plan --var-file=services/kubernetes.tfvars --var-file=services/network.tfvars --var-file=services/policy.tfvars --var-file=services/profile.tfvars --var-file=services/role.tfvars --var-file=services/vm.tfvars -json > PROJECT_ROOT/scopes/aws/single_scope/terraform/tf_plan.json \nin folder PROJECT_ROOT/scopes/aws/single_scope/terraform\n\nBash action terminated\nFinished tf action sucessfully\n'
    },
    "missing_tf_init" : {
        "aws/single_scope" : "Starting Cloud Tiger\nStarting Cloud Tiger action on simple scope config/aws/single_scope\nExecuting Terraform command apply\nBash action : terraform apply --var-file=services/kubernetes.tfvars --var-file=services/network.tfvars --var-file=services/policy.tfvars --var-file=services/profile.tfvars --var-file=services/role.tfvars --var-file=services/vm.tfvars\nExecution of command :\nterraform apply --var-file=services/kubernetes.tfvars --var-file=services/network.tfvars --var-file=services/policy.tfvars --var-file=services/profile.tfvars --var-file=services/role.tfvars --var-file=services/vm.tfvars > cloudtiger_std.log \nin folder PROJECT_ROOT/scopes/aws/single_scope/terraform\n\nError in the execution of command :\n[Errno 2] No such file or directory: 'PROJECT_ROOT/scopes/aws/single_scope/terraform'\n"
    }
}
