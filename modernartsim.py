# simulate Modern Art

# So many horrifying simplistic assumptions
# - All players have continuous perfect knowledge of everybody’s cash
# - All players have continuous access to an identical perfect oracle that tells them what the painting is going to be worth at the end
# - Only plays the first round (the one with max 30 value per painting)
# - Paintings are random order of 4x30, 3x20, 2x10 (9 paintings), not chosen strategically by players
# - Auction types are just combined and we simulate by taking the average of the two highest bids as the final price (sometimes seller-favored, sometimes buyer-favored, so we average it??)
# - Players always start with 100 cash and if they don't have enough to make their desired bid they bid their whole cash


import random
import math

class Player:
    name = None

    def step(self, state: dict) -> int:
        raise NotImplementedError


class P_Noop(Player):
    # never buys
    name = 'Noop'
    def step(self, state):
        return 0;

class P_Big(Player):
    # bids up to value of painting minus one dollar
    name = 'BigSpender'
    def step(self, state):
        return state['paintings'][-1]-1

class P_Even(Player):
    # bids half the painting value for an even split
    name = 'EvenSteven'
    def step(self, state):
        return state['paintings'][-1]//2

class P_Ratio(Player):
    # bids the proportion of the value that is passed in the constructor
    name = 'Ratio'

    def __init__(self, ratio):
        self.ratio = ratio
        self.name = 'Ratio'+str(ratio)
    def step(self, state):
        return math.floor(state['paintings'][-1] * self.ratio)

class P_MeVsYou(Player):
    # bids low if the seller is its top competitor and it is currently not winning, otherwise bids high
    name = 'MeVsYou'

    def step(self, state):
        player_ids = list(range(len(state['player_names'])))
        not_me_ids = list(filter(lambda x: state['player_names'][x] != self.name, player_ids))
        my_id = list(filter(lambda x: state['player_names'][x] == self.name, player_ids))[0]
        highest_competitor = not_me_ids[0]
        highest_competitor_score = None
        for n in not_me_ids:
            score = state['scores'][n]['cash'] + state['scores'][n]['painting_value']
            if highest_competitor_score is None or score > highest_competitor_score:
                highest_competitor_score = score
                highest_competitor = n
        my_score = state['scores'][my_id]['cash'] + state['scores'][my_id]['painting_value']
        seller_id = state['turn']
        if seller_id == highest_competitor and my_score <= highest_competitor_score:
            return math.floor(0.4 * state['paintings'][-1])
        return math.floor(0.8 * state['paintings'][-1])



class Game:

    def __init__(self, players, doprint=False):
        self.players = players
        self.doprint = doprint
        self.state = {
            'scores':{},
            'round':0,
            'turn':0,
            'paintings':[],
            'player_names': list(x.name for x in self.players)
        }
        for i in range(len(self.players)):
            self.state['scores'][i] = {
                'cash':100,
                'painting_value':0,
            }
        self.paintings = list(sorted([30]*4 + [20]*3 + [10]*2, key=lambda x: random.random()))

    def round(self, painting):
        self.state['paintings'] += [painting]

        high_bid = 0;
        second_bid = 0;
        buyer = -1
        seller = self.state['turn']
        if self.doprint:
            print('----------')
            print(f'it is {self.players[seller].name} turn to sell')
        for i in range(len(self.players)):
            if i == seller:
                continue
            curr_max_bid = min(self.state['scores'][i]['cash'], self.players[i].step(self.state))
            if curr_max_bid > high_bid:
                second_bid = high_bid
                high_bid = curr_max_bid
                buyer = i
            else:
                if curr_max_bid > second_bid:
                    second_bid = curr_max_bid
            if self.doprint:
                print(f'after {self.players[i].name} {curr_max_bid}: top is {self.players[buyer].name} with {high_bid} {second_bid}')
        if buyer >= 0:
            final_price = (high_bid + second_bid)//2
            self.state['scores'][buyer]['cash'] -= final_price
            self.state['scores'][seller]['cash'] += final_price
            self.state['scores'][buyer]['painting_value'] += self.state['paintings'][-1]
            if self.doprint:
                print(f'{self.players[seller].name} sold to {self.players[buyer].name} value {painting} for {final_price} on bids {high_bid} {second_bid}')
        self.state['round'] += 1
        self.state['turn'] = (self.state['turn'] + 1) % len(self.players)

        if self.doprint:
            self.print_state()


    def print_state(self):
        print(self.state['paintings'])
        for i in range(len(self.players)):
            p = self.players[i]
            ps = self.state['scores'][i]
            print(f"{p.name.rjust(20, ' ')}: {str(ps['cash']+ps['painting_value']).rjust(5, ' ')} (cash: {ps['cash']}, value: {ps['painting_value']})")

    def run(self):
        for i in range(len(self.paintings)):
            self.round(self.paintings[i])



def simulate(players, n):
    scores = {}
    for p in players:
        scores[p.name] = [0, 0, 0]
    for i in range(n):
        g = Game(players)
        g.run()
        curr_s = g.state['scores']
        for p in range(len(players)):
            name = players[p].name
            ps = curr_s[p]
            scores[name][1] += ps['cash']
            scores[name][2] += ps['painting_value']
            scores[name][0] += ps['cash'] + ps['painting_value']
    for p in players:
        for s in range(3):
            scores[p.name][s] /= n
    print()
    print('== AVERAGE SCORES =============')
    print('\t'.join(['player'.rjust(20, ' '), 'total', 'cash', 'paintings']))
    for p in sorted(players, key=lambda x: scores[x.name][0], reverse=True):
        print('\t'.join([p.name.rjust(20, ' ')]+[str(x) for x in scores[p.name]]))





if __name__ == '__main__':
    players = [
        P_Noop(),
        P_Big(),
        P_Even(),
        P_MeVsYou(),
        #P_Ratio(.66),
        #P_Ratio(.6)
    ]

    #Game(players, True).run()
    simulate(players, 10000)
