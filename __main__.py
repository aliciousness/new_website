
from run_website.run import Website



'''
IMPORTANT


Call Website argument first, and then run "check_validation" method after validating connection and certs to host zone through AWS console.


IMPORTANT
'''

init = Website(
    dns="omnifoodsolutions.com",
    repository_id="aliciousness/omnifood-project",
    provider_type="GitHub").check_validation("aliciousness")


