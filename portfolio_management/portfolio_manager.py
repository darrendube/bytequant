class PortfolioManager:
    def __init__(self, assets:list):
        '''
        Initialise the PortfolioManager. Pass in the assets it should consider ()

        Arguments
        ---------
        asset_types : list
            The list of asset types the portfolio manager should consider. Can be used to instruct PortfolioManager to 
            add or remove asset types
           

        '''
        self.asset_types = assets

    def evaluate(self, portfolio):

        # TODO: maybe first calculate portfolio's current risk premium
        
        # Without regarding asset types, determine general target risk profile of portfolio
        general_risk_pr = [1/3, 1/3, 1/3] # low risk, medium risk, high risk
        # Simple implementation for now, can make it more complicated in the future
        outlook = self.get_economic_outlook()
        if outlook == 'positive': # weight portfolio more to hish risk
            general_risk_pr = [0.1, 0.3, 0.6]
        elif outlook == 'neutral':
            general_risk_pr = [1/3, 1/3, 1/3]
        elif outlook == 'negative':
            general_risk_pr = [0.6, 0.3, 0.1]

        # TODO: Now allocate the risk profiles to different assets. For now, will only have equities. 
        #    TODO: consider self.asset_types and allocate risk equally between the assets
        #    TODO: make sure the floats in instr add up to 1!!!
        instr = {'equity': general_risk_pr,
                 'fixed_income': [0,0,0],
                 'forex': [0,0,0],
                 'cash_buffer': 0.0}
        return instr
    
    def get_economic_outlook(self):
        '''
        Using sentiment analysis, economic data from the fed (taking into account how recently it was released)

        outlook can be 'positive', 'neutral', 'negative'
        '''

        # TODO: finish this
        return 'positive'