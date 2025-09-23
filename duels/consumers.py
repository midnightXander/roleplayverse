from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from django.shortcuts import get_object_or_404

from api.models import PushSubscription
from battles.views import _reward_player
from users.views import _player_data
from .utility import seconds_difference
from battles.models import BASIC_ACTIONS
from battles.solo_battle import _evaluate_duel_actions, _log_actions
from duels.models import Duel, DuelAction, DuelFighter
from duels.views import _duel_data, last_fighter_action
from users.models import Player
from api.utility import send_push_notification




class DuelConsumer(AsyncWebsocketConsumer):
    from channels.db import database_sync_to_async
    
    @database_sync_to_async
    def perform_duel_action(self, duel_code, action):
        player = get_object_or_404(Player, user=self.scope["user"])
        duel = Duel.objects.filter(code=duel_code).first()
        current_fighter = DuelFighter.objects.filter(duel=duel, player=player).first() if duel else None
        opponent_fighter = DuelFighter.objects.filter(duel=duel).exclude(player=player).first() if duel else None

        fighter1 = DuelFighter.objects.filter(duel=duel).first() if duel else None
        fighter2 = DuelFighter.objects.filter(duel=duel).last() if duel else None

        
        last_current_fighter_action = last_fighter_action(current_fighter)
        seconds_diff =   seconds_difference(last_current_fighter_action.created_at) if last_current_fighter_action else 0
        
        print(seconds_diff, last_current_fighter_action)
        if duel.winner:
            return {'message': 'This duel is already terminated.', 'status':'error'}
        
        if last_current_fighter_action : #and seconds_diff < 500
            return {'message': 'You already performed an action, wait for your opponent.', 'status':'error'}



        player_character = current_fighter.character if current_fighter else None
        opponent_character = opponent_fighter.character if opponent_fighter else None
        possible_actions = BASIC_ACTIONS + player_character['jutsus']
        
        player_action = BASIC_ACTIONS[0]

        def get_action(action , possible_actions):
            for act in possible_actions:
                if act['name'] == action: 
                    return act 
                
                
        player_action = get_action(action, possible_actions)         
        new_duel_action = DuelAction.objects.create(fighter = current_fighter, action = player_action)
        new_duel_action.save()

        #if last_fighter_action(opponent_fighter) and seconds_diff >= 15 else get_action('Defend', BASIC_ACTIONS)
        opponent_action = last_fighter_action(opponent_fighter) 
        
        # if not opponent_action and seconds_diff >= 500:
        #     opponent_action =  DuelAction.objects.create(fighter = opponent_fighter, evaluated = True, action = get_action('Defend', BASIC_ACTIONS))
        #     opponent_action.save()

        logs = json.loads(duel.log)
        if opponent_action:
            print("evaluating :", player_action.get('name') , " against " ,opponent_action.action.get('name'))
            new_logs = _log_actions(player_action, opponent_action.action, player_character, opponent_character)
            for log in new_logs:
                logs.append(log)
            
            fighter1_character, fighter2_character, new_logs, winner =  _evaluate_duel_actions(fighter1.character, fighter2.character, last_fighter_action(fighter1).action, last_fighter_action(fighter2).action)
            fighter1.character = fighter1_character
            fighter2.character = fighter2_character
            fighter1.save()
            fighter2.save()
            
            opponent_action.evaluated = True
            new_duel_action.evaluated = True
            opponent_action.save()
            new_duel_action.save()
            logs = logs + new_logs
            

            if winner:
                winner_fighter = fighter1 if fighter1.character.get('name') == winner else fighter2
                duel.winner = winner_fighter.player
                duel.status = "finished"
                duel.ended_at = datetime.now()
                rewards = _reward_player(winner_fighter.player)

            # rewards = {'xp' : 0, }
            winner_data = { 'player' : _player_data(winner_fighter.player) }  if winner else None
            if winner_data:
                winner_data['character'] = winner_fighter.character 
            
        else:
            return {'status':'waiting','message': 'waiting for opponent...'}        
            
        duel.log = json.dumps(logs)
        duel.save()  

        return {'status': 'continue', 'battle_logs': logs, 'player_character': fighter1_character, 'opponent_character': fighter2_character, 'winner': winner_data, 'rewards': []}

    @database_sync_to_async
    def duel_data(self, duel_code):
        duel = Duel.objects.filter(code=duel_code).first()
        return _duel_data(duel)

    @database_sync_to_async
    def alert_opponent(self, duel_code):    
        player = get_object_or_404(Player, user=self.scope["user"])
        duel = Duel.objects.filter(code=duel_code).first()
        current_fighter = DuelFighter.objects.filter(duel=duel, player=player).first() if duel else None
        opponent_fighter = DuelFighter.objects.filter(duel=duel).exclude(player=player).first() if duel else None
        if opponent_fighter:
            payload = {
                            'title': f'Ton duel peut commencer !',
                            'body': f'{current_fighter.player} a rejoint ton duel. Que le meilleur gagne',
                            #'icon': f'{player.profile_picture.url}',
                            'url': f'/duels/{duel_code}'
                        }
            send_push_notification(PushSubscription.objects.filter(user = opponent_fighter.player.user).last(), payload, opponent_fighter.player.user)

    
    async def connect(self):
        self.user = self.scope["user"]
        self.duel_code = self.scope["url_route"]["kwargs"]["duel_code"]
        self.group_name = f"duel_{self.duel_code}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):

        data = json.loads(text_data)
        action_type = data.get('type')
        if action_type == 'joined':
            #dispatch joined
            duel = await self.duel_data(self.duel_code)
            if duel.get('status') == 'pending':
                await self.alert_opponent(self.duel_code)
                await self.channel_layer.group_send(
                    self.group_name,{
                        "type": "joined",
                        'user': self.user.username,
                    }
                ) 
        elif action_type == "duel_action":    
            action = data.get('action')
            
            result = await self.perform_duel_action(self.duel_code, action)

            # await self.send(text_data=json.dumps({
            #     "type": "duel_action",
            #     "status": result.get('status', 'error'),
            #     "message": result.get('message'),
            #     "battle_logs": result.get('battle_logs', []),
            #     "player_character": result.get('player_character', {}),
            #     "opponent_character": result.get('opponent_character', {}),
            #     "winner": result.get('winner'),
            #     "rewards": result.get('rewards', []),
            # }))
            #return
            await self.channel_layer.group_send(
                self.group_name,{
                    "type": "duel_action",
                    "action": action,
                    'user': self.user.username,
                    "status": result.get('status', 'error'),
                    "message": result.get('message'),
                    "battle_logs": result.get('battle_logs', []),
                    "player_character": result.get('player_character', {}),
                    "opponent_character": result.get('opponent_character', {}),
                    "winner": result.get('winner'),
                    "rewards": result.get('rewards', []),

                }
            ) 
       

    async def duel_action(self,event):
        action = event['action']
        user = event['user']

        await self.send(text_data=json.dumps({
            "type" : 'duel_action',
            "action": action,
            "user": user,
            "status": event.get('status', 'error'),
            "message": event.get('message'),
            "battle_logs": event.get('battle_logs', []),
            "player_character": event.get('player_character', {}),
            "opponent_character": event.get('opponent_character', {}),
            "winner": event.get('winner'),
            "rewards": event.get('rewards', []),

        }))

    async def joined(self,event):
        user = event['user']

        await self.send(text_data=json.dumps({
            "type" : 'joined',
            "user": user,
        }))    
           

        