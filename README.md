Discord_Bot_Music

Discord Bot playing YouTube links.
Missing Files:

    First File: .env
    This file contains your Discord Token.
    Example content for .env file:

    discord_token=#Enter your token

    Second File: cookies.txt
    This file contains exported cookies, which are required for authenticating access to YouTube videos (especially age-restricted or region-locked content).
    How to Export Cookies:

    To create the cookies.txt file, follow these steps:

        Install a browser extension for exporting cookies.
            For Google Chrome or Edge: Use EditThisCookie or similar tools.
            For Firefox: Use the Cookies.txt extension.

        Visit YouTube.
        Log into your YouTube account to ensure that your cookies include all necessary authentication data.

        Export Cookies.
            Open the extension.
            Select the option to export cookies in the .txt format.
            Save the file as cookies.txt in the same directory as your Discord bot script.

        Verify Cookies.
        Make sure the cookies.txt file includes entries for youtube.com.

With these two files in place, your Discord bot will be able to authenticate and play YouTube links seamlessly.
