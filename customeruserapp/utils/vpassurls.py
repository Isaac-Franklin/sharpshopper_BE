
from optparse import Option

class vpassUrls():
    mtndata = 'https://sandbox.vtpass.com/api/service-variations?serviceID=mtn-data'
    mtndata_live = 'https://vtpass.com/api/service-variations?serviceID=mtn-data'
    mtnvvtu_live = 'https://vtpass.com/api/pay'
    mtnvtu_test = 'https://sandbox.vtpass.com/api/pay'
    
    # 
    verify_mter_number_live ='https://vtpass.com/api/merchant-verify'
    verify_mter_number_test ='https://sandbox.vtpass.com/api/merchant-verify'   
     
    # prepaid and postpaid meter payment
    meterpayment_live ='https://vtpass.com/api/pay'
    meterpayment_test ='https://sandbox.vtpass.com/api/pay' 
    


class CableTCSubscriptionAlgo:
    def __init__(self, option: str):
        self.option = option

    @property
    def checkdstvplans_live(self):
        return f"https://vtpass.com/api/service-variations?serviceID={self.option}"

    @property
    def checkdstvplans_test(self):
        return f"https://sandbox.vtpass.com/api/service-variations?serviceID={self.option}"
    
    # 
    # 
    verifysmartcardnumber_live ='https://vtpass.com/api/merchant-verify'
    verifysmartcardnumber_test ='https://sandbox.vtpass.com/api/merchant-verify'
    
    # 
    cableTVBoquestRenewal_live ='https://vtpass.com/api/pay'
    cableTVBoquestRenewal_test ='https://sandbox.vtpass.com/api/pay' 
    



