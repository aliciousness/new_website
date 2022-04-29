"""An AWS Python Pulumi program"""
import pulumi
from run_website.run import Website
import os 


'''
IMPORTANT


call Website argument first, and then run "run_website" method after validating connection and certs to host zone through AWS console


IMPORTANT
'''

# init = Website(
#     dns="richardcraddock.me",
#     repository_id="aliciousness/resume",
#     provider_type="GitHub")




# while True:
#     try:
#         cert_validation = input("Are both certificates validated and records created in AWS Route 53? y or n: ")

#         connection_validation = input("Is the connection status available? y or n: ")
#     except EOFError:
#         break
    
#     if cert_validation == 'y' and connection_validation =='y':
#         init.run_website()
#         break
#     else:
#         print("please validate the proper resources. to continue forward")