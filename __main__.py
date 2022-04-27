"""An AWS Python Pulumi program"""
import pulumi
from run_website.run import Website

'''IMPORTANT


fill arguments for website first, and then run "run_website" method after validating connection and certs to host zone through AWS console


IMPORTANT'''

init = Website(
    dns="richardcraddock.me",
    repository_id="aliciousness/resume",
    provider_type="GitHub")

# init.run_website()