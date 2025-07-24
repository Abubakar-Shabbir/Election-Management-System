import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Count
from .models import Voter, Vote, Candidate
from channels.db import database_sync_to_async


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("admin_dashboard", self.channel_name)
        await self.accept()
        await self.send_dashboard_data()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admin_dashboard", self.channel_name)

    async def receive(self, text_data):
        pass  # You can handle commands from frontend here

    async def send_dashboard_data(self):
        total_voters = await self.get_total_voters()
        voted_count = await self.get_voted_count()
        not_voted = total_voters - voted_count

        vote_data = await self.get_constituency_data()

        await self.send(text_data=json.dumps({
            'total_voters': total_voters,
            'voted_count': voted_count,
            'not_voted_count': not_voted,
            'constituency_votes': vote_data,
        }))

    async def dashboard_update(self, event):
        await self.send_dashboard_data()

    @database_sync_to_async
    def get_total_voters(self):
        return Voter.objects.count()

    @database_sync_to_async
    def get_voted_count(self):
        return Vote.objects.values('voter').distinct().count()

    @database_sync_to_async
    def get_constituency_data(self):
        data = Vote.objects.values('candidate__constituency__region') \
                .annotate(total_votes=Count('id')) \
                .order_by('-total_votes')
        return [{'label': item['candidate__constituency__region'], 'votes': item['total_votes']} for item in data]
