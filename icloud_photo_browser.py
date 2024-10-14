import pandas as pd
from datetime import datetime
from pyicloud import PyiCloudService
api = PyiCloudService('email@domain.com', 'password')

## If you have 2FA enabled, this will let you enter the code you get on a device of your choice

if api.requires_2fa:
    print("Two-factor authentication required.")
    code = input("Enter the code you received of one of your approved devices: ")
    result = api.validate_2fa_code(code)
    print("Code validation result: %s" % result)

    if not result:
        print("Failed to verify security code")
        sys.exit(1)

    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = api.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
elif api.requires_2sa:
    import click
    print("Two-step authentication required. Your trusted devices are:")

    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print(
            "  %s: %s" % (i, device.get('deviceName',
            "SMS to %s" % device.get('phoneNumber')))
        )

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not api.send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = click.prompt('Please enter validation code')
    if not api.validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)

## Create a photo DataFrame by iterating through every photo/video in your library

photo_df = pd.DataFrame()

for photo in api.photos.all:
    name = photo.filename
    size = photo.size / 1000000 # MB
    created_date = ''.join([str(photo.created.year), '-', str(photo.created.month), '-', str(photo.created.day)])
    
    row = pd.DataFrame([[size, created_date]], index=[name])  ## Create a DataFrame for the new row
    photo_df = pd.concat([photo_df, row])  ## Concatenate the new row to the DataFrame


## Display the DataFrame, largest files on top

photo_df.rename(columns={0:'size_MB', 1:'cretd_dt'}, inplace=True)
photo_df.reset_index(inplace=True, names='file_nm')
photo_df.sort_values(by='size_MB', ascending=False, inplace=True)
photo_df
