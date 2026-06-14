from reverie_sdk import ReverieClient

def transliterate_text(data, target_language):
    client = ReverieClient(
        api_key="d413a11c507598ec4851aeee5451e0c93de54f19",
        app_id="dev.naveenpainthouse",
    )
    
    res = client.t13n.transliteration(
        data=data,
        src_lang="en",
        cnt_lang="en",
        tgt_lang=target_language,
        noOfSuggestions=1,
    )
    
    return [item.outString[0] for item in res.responseList]

if __name__ == "__main__":
    data = [
        "Reverie Language Technologies is located in Bengaluru",
        "The address is Jio Avana, Bellandur, Bengaluru -560102",
        "The website address is www.reverieinc.com.",
    ]
    target_language = "hi"  # Hindi
    translated_data = transliterate_text(data, target_language)
    print(translated_data)
