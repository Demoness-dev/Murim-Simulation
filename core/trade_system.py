import uuid
from core.globals import DONE_TRADES
from utils.logger import logger


class TradeSystem:
    def __init__(self, node_map):
        self.map = node_map
        self.pending_trades = {}  # uuid: trade_data
        self.completed_trades = {}  # uuid: trade_data

    def register_trade(self, origin_city, resource, offered_amount, amount, desired_resource):
        trade_id = uuid.uuid4()
        trade_data = {
            "id": trade_id,
            "origin": origin_city,
            "resource": resource,
            "offered amount": offered_amount,
            "desired amount": amount,
            "desired_resource": desired_resource,
            "status": "pending"
        }
        self.pending_trades[trade_id] = trade_data
        logger.execute("Trade Registered", "info", f"{origin_city.name} offers {amount} {resource} for {desired_resource}")
        return trade_id

    def find_matching_trade(self, buyer_city):
        for trade_id, trade in list(self.pending_trades.items()):
            origin = trade["origin"]
            if origin == buyer_city:
                continue  # can't trade with yourself

            if self.evaluate_trade(buyer_city, trade):
                self.execute_trade(buyer_city, trade)
                self.completed_trades[trade_id] = trade
                del self.pending_trades[trade_id]
                return trade_id
        return None  # no viable trade found

    def evaluate_trade(self, buyer_city, trade):
        desired = trade["desired_resource"]
        offered = trade["resource"]
        amount = trade["desired amount"]

        if buyer_city.resources.get(desired, 0) < amount:
            return False

        if not buyer_city.resource_trigger_check(offered):
            return False
        
        return True

    def execute_trade(self, buyer_city, trade):
        origin_city = trade["origin"]
        amount = trade["desired amount"]
        offered_amount = trade["offered amount"]
        res_offered = trade["resource"]
        res_desired = trade["desired_resource"]

        # Resource exchange
        buyer_city.remove_resources(amount, res_desired)
        buyer_city.add_resource(res_offered, offered_amount)

        origin_city.remove_resources(offered_amount, res_offered)
        origin_city.add_resource(res_desired, amount)

        trade["status"] = "completed"
        logger.execute("Trade Executed", "info",
                       f"{origin_city.name} exchanged {amount} {res_offered} with {buyer_city.name} for {res_desired}")
