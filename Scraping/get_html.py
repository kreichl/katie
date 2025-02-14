from urllib.request import Request, urlopen
import io
import os
import gzip
from bs4 import BeautifulSoup

# url = "https://www.realtor.com/realestateandhomes-detail/5625-N-57th-St_Milwaukee_WI_53218_M94508-52688"
# url = "	https://www.realtor.com/realestateandhomes-search/Waukesha_WI/type-single-family-home,condo,townhome/nc-hide/dom-10"
# url = "https://www.redfin.com/city/2575/WI/Brookfield/filter/property-type=house+condo+townhouse,status=active"
# url = "https://www.redfin.com/county/3230/WI/Waukesha-County/filter/property-type=house+condo+townhouse,max-days-on-market=1d,include=forsale,status=active"
url = "https://www.trulia.com/home/382-oneida-st-delafield-wi-53018-59900542"

title = os.path.splitext(os.path.basename(url))[0]


# headers = {
#   "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#   "accept-encoding": "gzip, deflate, br, zstd",
#   "accept-language": "en-US,en;q=0.9",
#   "cache-control": "max-age=0",
#   "cookie": "split=n; split_tcv=187; __ssn=65b2d90f-1564-474e-9f2d-506b1a5c9c8c; __ssnstarttime=1739410188; __vst=387ad2ba-700b-4e38-b131-da9aa731e640; __bot=false; _pbjs_userid_consent_data=3524755945110770; criteria=sprefix%3D%252Fnewhomecommunities%26area_type%3Dcity%26city%3DBrookfield%26pg%3D1%26state_code%3DWI%26state_id%3DWI%26loc%3DBrookfield%252C%2520WI%26locSlug%3DBrookfield_WI%26county_fips%3D55133%26county_fips_multi%3D55133; isAuth0GnavEnabled=V1; _lr_retry_request=true; _lr_env_src_ats=false; permutive-id=e55e1700-2973-4c9f-8315-0266932c5e6a; __split=13; ab.storage.userId.7cc9d032-9d6d-44cf-a8f5-d276489af322=g%3Avisitor_387ad2ba-700b-4e38-b131-da9aa731e640%7Ce%3Aundefined%7Cc%3A1739410190840%7Cl%3A1739410190841; ab.storage.deviceId.7cc9d032-9d6d-44cf-a8f5-d276489af322=g%3A523430fc-c80b-af94-9591-521f814e49b9%7Ce%3Aundefined%7Cc%3A1739410190843%7Cl%3A1739410190843; ab.storage.sessionId.7cc9d032-9d6d-44cf-a8f5-d276489af322=g%3A65af7633-f3d4-9181-7c34-5c595011366e%7Ce%3A1739411990850%7Cc%3A1739410190841%7Cl%3A1739410190850; pxcts=04ba6755-e9aa-11ef-8ff9-9c34e91cfe47; _pxvid=04ba5c88-e9aa-11ef-8ff9-9207aadfb808; KP_UIDz-ssn=0EYjEOzydyQjkruyk50bdn00troWu0jf8NQ0JyHUrSvk3dMeZNIvake8jC1XLhjUm3AwbVql4eGu951hQBttxgfirbLUtl9fPG1ZODVV0YSXGq0W2zJNjr3Jzs4mBznvtYvg0CdshheeIuONnf7w2061P24NJbbmT2R5up3o; KP_UIDz=0EYjEOzydyQjkruyk50bdn00troWu0jf8NQ0JyHUrSvk3dMeZNIvake8jC1XLhjUm3AwbVql4eGu951hQBttxgfirbLUtl9fPG1ZODVV0YSXGq0W2zJNjr3Jzs4mBznvtYvg0CdshheeIuONnf7w2061P24NJbbmT2R5up3o; __gsas=ID=0f47f40c4f546ae1:T=1739410190:RT=1739410190:S=ALNI_MYujNKyRrkxOnlfFdIK0hSAKW7EEQ; AMCVS_8853394255142B6A0A4C98A4%40AdobeOrg=1; _gcl_au=1.1.1343698365.1739410191; _fbp=fb.1.1739410191457.3862121616349380; s_ecid=MCMID%7C19625737951068610982092992728681768496; _ncg_sp_ses.cc72=*; _ncg_sp_id.cc72=c941400a-1f55-44d5-8c72-2c2dc7a48834.1739410192.1.1739410192.1739410192.1cfd3f3a-cd1c-4e0b-89c8-2cd20e5f07e6; _ncg_id_=c941400a-1f55-44d5-8c72-2c2dc7a48834; _ga=GA1.1.543272243.1739410192; AMCVS_AMCV_8853394255142B6A0A4C98A4%40AdobeOrg=1; AMCV_AMCV_8853394255142B6A0A4C98A4%40AdobeOrg=-1124106680%7CMCMID%7C19625737951068610982092992728681768496%7CMCIDTS%7C20133%7CMCOPTOUT-1739417391s%7CNONE%7CvVersion%7C5.2.0; AMCV_8853394255142B6A0A4C98A4%40AdobeOrg=-1124106680%7CMCIDTS%7C20133%7CMCMID%7C19625737951068610982092992728681768496%7CMCAAMLH-1740014990%7C7%7CMCAAMB-1740014990%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1739417391s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-20140%7CvVersion%7C5.2.0; _ncg_domain_id_=c941400a-1f55-44d5-8c72-2c2dc7a48834.1.1739410191501.1802482191501; adcloud={%22_les_v%22:%22c%2Cy%2Crealtor.com%2C1739411992%22}; _cq_duid=1.1739410192.uNqJMNoqd2pRDsBW; _cq_suid=1.1739410192.WXnyLk2oX9hILXVv; _ncg_g_id_=3b8d1607-fd7d-4ef6-b5fb-45215fd2b336.1.1739410191.1802482191501; ajs_anonymous_id=197bf6e3-f7ad-4c33-b957-53c570cdc3b2; crto_is_user_optout=false; __qca=P0-51292526-1739410192236; __gads=ID=b72e5a4411d2e88f:T=1739410191:RT=1739410191:S=ALNI_Mauc8rqvMH-e6b-qHqreftGZ0MQGg; __gpi=UID=00001048412f4174:T=1739410191:RT=1739410191:S=ALNI_MaeJDf-Tz_npUiZuACgddBpLMPaJQ; __eoi=ID=fb235eb1bb737b87:T=1739410191:RT=1739410191:S=AA-AfjYTP5tUD52Kw2-hJiF0OXCI; _ga_GKXRF889HV=GS1.1.1739410191.1.0.1739410193.0.0.656439601; _uetsid=05976d80e9aa11ef88d28904b544f683|1aafn81|2|fte|0|1870; _uetvid=05978590e9aa11ef84e6d1bcf3bcca21|15beomc|1739410192747|1|1|bat.bing.com/p/insights/c/t; _px3=d933823a5ede2caf2bc0c29cc8f5a953e69523b81deccb44dd7e604974978d58:JL4Kx4vPr7gCfFt0pu3AQjmeNKE6A7YQSMlGR5SwTkYkrNm314otl1Pk8TJyXF91JrwUizl/9PpFazq3TQoHVg==:1000:nV65XpgMcLJF00kYEOwk6KBTHGZ7bgZgyY1OpFtcNTFitBW3yf69oifSqfnoVsPZOvTXQodPGrC/kk/DWjVNOWxkz7bwaQCkNTXSGWeBN6Ox0FsOdZNkK0QjCQj1seIBeiYtXWGRFQfZQjfR6UNVBEwR1EPzkAcwG5tU7Wzlbv0E6Qnk7Cap2FCNy8LMcP0Kq29EdSwXguTaZDYr5fIL/cVFJFqkVvCgxulR4mdi5pI=; kampyle_userid=ab73-a6f6-814d-0ad3-dd71-e225-3129-ecca; kampyleUserSession=1739410193880; kampyleUserSessionsCount=1; kampyleSessionPageCounter=1; kampyleUserPercentile=44.95721678034381; panoramaId_expiry=1740014994175; _cc_id=fdf4dbc8fe375fb1aef7624ba1d8618e; panoramaId=4138dab9ef5655432a130d1ae2da185ca02cc487beb15b74b7930371dbfa4384; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://www.realtor.com/realestateandhomes-search/Brookfield_WI/type-single-family-home%2Ccondo%2Ctownhome/nc-hide/dom-1%22%2C%22sref%22:%22%22%2C%22sts%22:1739410195926%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=607646d5-3745-4f9e-8ef8-6f7af00bcf64%22%2C%22session_count%22:1%2C%22last_session_ts%22:1739410195926}; _lr_sampling_rate=100; _lr_geo_location_state=WI; _lr_geo_location=US; cto_bundle=pormdl9kZiUyQjhad0JldTlucWRPMmNJdVhZNGJVMCUyQnp0VTVOTUIlMkZOc204VFJvcFRZUHFyR2w4U0RlRzl1RFMlMkJNVjVMZnJFNWlSRiUyQm5RQUdpc0pna3dWZ1pMWGZhVjgwVktPN3dNNFd1bVdWM200QXdjNzBQNkZLQ1hJRTQ4aGVUb3dOOFI; _ga_MS5EHT6J6V=GS1.1.1739410191.1.0.1739410196.55.0.0",
#   "priority": "u=0, i",
#   "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
#   "sec-ch-ua-mobile": "?0",
#   "sec-ch-ua-platform": "\"Windows\"",
#   "sec-fetch-dest": "document",
#   "sec-fetch-mode": "navigate",
#   "sec-fetch-site": "same-origin",
#   "sec-fetch-user": "?1",
#   "upgrade-insecure-requests": "1",
#   "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
# }

headers = {
  "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
  "accept-encoding": "gzip, deflate, br, zstd",
  "accept-language": "en-US,en;q=0.9",
  "cache-control": "max-age=0",
  "cookie": "_pxhd=KauQE3rj4IByelFk57a15O8GLkTaFC-R4-4-VRFu6g2jxDalJcm3y3lDiPOmbuKUkvpx43bzA-5WSD4S3KWrcQ==:6K8HEjCfJtgTAa7VwqF/qDVFuAc/S8n-EwcqLnnDP2hSpAxRI4FwcNa/AAzlDx0fg6J/dGXsfHthpHOcTeu7BXqmtVS4mph7BUeTUvBND7Q=; _csrfSecret=pVGc5NHeGd82qWDY9sB%2FMc8e; tlftmusr=250214srognl2xpkwisl8yiyjpjqm349; tabc=%7B%221274%22%3A%22control%22%2C%221337%22%3A%22b%22%2C%221353%22%3A%22b%22%2C%221386%22%3A%22b%22%2C%221395%22%3A%22b%22%2C%221406%22%3A%22control%22%2C%221409%22%3A%22b%22%2C%221422%22%3A%22control%22%2C%221425%22%3A%22a%22%2C%221437%22%3A%22a%22%2C%221439%22%3A%22a%22%2C%221440%22%3A%22b%22%2C%221464%22%3A%22a%22%2C%221469%22%3A%22a%22%2C%221478%22%3A%22control%22%2C%221484%22%3A%22a%22%2C%221485%22%3A%22b%22%2C%221486%22%3A%22a%22%2C%221493%22%3A%22a%22%2C%221505%22%3A%22control%22%2C%221506%22%3A%22b%22%7D; trul_visitTimer=1739543889928_1739543889928; zjs_user_id=null; zg_anonymous_id=%22c60721f0-a0f5-42f5-b284-db027ab2d3f0%22; zjs_anonymous_id=%22250214srognl2xpkwisl8yiyjpjqm349%22; s_fid=54898FE260F32E84-0620595F1D2A48A0; s_cc=true; _lr_retry_request=true; _lr_env_src_ats=false; s_vi=[CS]v1|33D7AAA9338271EA-4000162C290C2FE5[CE]; pxcts=503e4b5f-eae1-11ef-9fe4-efdabaf14bfc; _pxvid=4f54318f-eae1-11ef-be1b-be684dd85b91; __gads=ID=99c387aef4b29637:T=1739543891:RT=1739543891:S=ALNI_MbrpUhxBW7Jm_rRI5LrTOD7_o0caQ; __gpi=UID=0000104ba07a7417:T=1739543891:RT=1739543891:S=ALNI_MbLNWMJsoHRyAqGRigXeNj4W3VD_Q; __eoi=ID=f453775c871e202d:T=1739543891:RT=1739543891:S=AA-Afjauzzl2sj07Jgy_FqK8fbSl; _px3=818b63dadf27d7ce0833e24653086403cc931a28682b5b5390585d05261ed7ce:m+i8wfLgr/8rXOAWBMOstHcNhPkyTlmyqRgBEhVOb2iP7Cr757kEBHb1FSDVCTom57nSn0pp9+2RZOy4e1NW/w==:1000:8EcQJviTIOpo//sD9uRIT71f1JxIlGNP3cO8WIpRW1Auln7LvtKLvJo+s5ZruZ1GRHNNAD0dDEW9QgRf1CLKHo0UzPETUZ2p9zo/z7HQlRpdZconqKynYtfEVLhyRhHh5NP2+is4EUYiTuJFqlnX+iCi8JWSClohEDD2mKwtskNrZtsREAbaXpNX1Z8GU8QwidokOCtmgoAbhb7eoX3muJsiw3cwSHRYCiV8JwBqL/s=; _lr_sampling_rate=100; _lr_geo_location_state=WI; _lr_geo_location=US; s_sq=truliacom%3D%2526c.%2526a.%2526activitymap.%2526page%253Dbuy%25253Apdp%25253Aoverview%2526link%253DSkip%252520main%252520navigation%252520Buy%252520Rent%252520Mortgage%252520Saved%252520Homes%252520Saved%252520Searches%252520Sign%252520up%252520or%252520Log%252520in%252520Back%252520to%252520Search%252520For%252520Sale%252520WI%252520Delafield%25252053018%2525203%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dbuy%25253Apdp%25253Aoverview%2526pidt%253D1%2526oid%253Dfunctionrg%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DDIV; g_state=googleOneTap",
  "priority": "u=0, i",
  "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": "\"Windows\"",
  "sec-fetch-dest": "document",
  "sec-fetch-mode": "navigate",
  "sec-fetch-site": "same-origin",
  "sec-fetch-user": "?1",
  "upgrade-insecure-requests": "1",
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}

request = Request(url, headers=headers)

# Open the URL
with urlopen(request) as response:
    # Check if the response is compressed
    if response.info().get("Content-Encoding") == "gzip":
        with gzip.GzipFile(fileobj=io.BytesIO(response.read())) as gzipped_file:
            html = gzipped_file.read().decode("utf-8")
    else:
        html = response.read().decode("utf-8")

# Save the response to a file
with open(f"Scraping/HTML_files/{title}.html","w", encoding="utf-8") as save_file:
    save_file.write(html)

soup = BeautifulSoup(html, "html.parser")

text = soup.get_text()

with io.open(os.path.join("Scraping", "text_files", f"{title}.txt"), "w", encoding="utf-8") as f:
    f.write(text)