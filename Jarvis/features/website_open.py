import webbrowser

def website_opener(domain):
    try:
        if ".com" not in domain:
            domain = domain + ".com"
        url =  domain
        webbrowser.open(url)
        return True
    except Exception as e:
        print(e)
        return False