
'''If Connecting Using FB
import fb_auth_token
fb_username = "fill with fb username"
fb_password = "fill with fb password"
fb_access_token = fb_auth_token.get_fb_access_token(fb_username, fb_password)
fb_user_id = fb_auth_token.get_fb_id(fb_access_token)
'''

host = 'https://api.gotinder.com'
#leave tinder_token empty if you don't use phone verification

## Lucas' Info
tinder_token = "36d64667-39f6-4ddc-b541-f7ae3b5c213d"
#_id: 5d0081523f4ac515009490af
##

## Matheus' Info
# tinder_token = "d404d139-69cb-43de-b4f5-3f6dcb0330e1"
#_id: 531f5b525322c5b615001bc1

# Your real config file should simply be named "config.py"
# Just insert your fb_username and fb_password in string format
# and the fb_auth_token.py module will do the rest!


