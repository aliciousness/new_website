from run_website.run import Website



'''
IMPORTANT


Call Website argument first, and then run "check_validation" method after validating connection and certs to host zone through AWS console.


IMPORTANT
'''

init = Website(
    dns="richardcraddock.me",
    repository_id="aliciousness/resume",
    provider_type="GitHub").check_validation()


