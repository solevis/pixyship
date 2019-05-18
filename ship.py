from itertools import groupby
from operator import itemgetter

from ps_client import PixelStarshipsApi


class Ship:
    # Represents a ship

    psa = PixelStarshipsApi()

    def __init__(self, name):
        self.name = name
        self.upgrades = []

    def add_upgrade(self, description, amount, currency, construction_time):
        self.upgrades.append(
            dict(description=description, amount=amount, currency=currency, seconds=construction_time)
        )

    def summarize(self, user_id=None):
        user_id = user_id or self.psa.get_user_id(self.name)
        if not user_id:
            return None, None, None, None, None, None
        data = self.psa.inspect_ship(user_id)
        if 'InspectShip' in data:   # Only seen on admin players so far
            return None, None, None, None, None, None
        return self.summarize_ship(data)

    def summarize_ship(self, data):
        user_d = data['ShipService']['InspectShip']['User']
        ship_d = data['ShipService']['InspectShip']['Ship']
        user = dict(
            id=user_d['@Id'],
            name=user_d['@Name'],
            sprite=self.psa.sprite_data(int(user_d['@IconSpriteId'])),
            alliance_name=user_d.get('@AllianceName'),
            alliance_sprite=self.psa.sprite_data(int(user_d.get('@AllianceSpriteId'))),
            trophies=int(user_d['@Trophy']),
            last_date=user_d['@LastAlertDate'],
        )

        ship_id = int(ship_d['@ShipDesignId'])
        immunity_date = ship_d['@ImmunityDate']
        ship_level = self.psa.ship_map[ship_id]['level']

        char_list = ship_d['Characters']['Character'] if ship_d['Characters'] else []
        if type(char_list) is not list:
            char_list = [char_list]

        chars = [self.get_char(x, ship_level, i + 1) for i, x in enumerate(char_list)]

        room_sorted_chars = sorted(chars, key=itemgetter('room_id'))
        chars_by_room = {k: list(v) for k, v in groupby(room_sorted_chars, key=itemgetter('room_id'))}
        rooms = [
            dict(
                self.psa.interiorize(int(x['@RoomDesignId']), ship_id),
                design_id=int(x['@RoomDesignId']),
                id=int(x['@RoomId']),
                row=int(x['@Row']),
                column=int(x['@Column']),
                chars=list(chars_by_room.get(int(x['@RoomId']), [])),
                construction=bool(x['@ConstructionStartDate']),
                upgradable=self.psa.is_room_upgradeable(int(x['@RoomDesignId']), ship_id),
            )
            for x in ship_d['Rooms']['Room']
        ]

        for c in chars:
            if c['upgradable']:
                cost = self.psa.char_gas[c['level']] * (1 - self.psa.ship_level_to_discount[ship_level] / 100)
                self.add_upgrade(c['name'], cost, 'gas', 0)

        for r in rooms:
            if r['upgradable']:
                upgrade = self.psa.get_upgrade_room(r['design_id'])
                if upgrade:
                    cost = upgrade['upgrade_cost']
                    self.add_upgrade(
                        r['name'], cost, upgrade['upgrade_currency'], upgrade['upgrade_seconds'])

        ship = dict(
            self.psa.ship_map[ship_id],
            power_use=sum([r['power_use'] for r in rooms]),
            power_gen=sum([r['power_gen'] for r in rooms]),
            shield=sum([r['capacity'] for r in rooms if r['type'] == 'Shield']),
            char_hp=sum([c['hp'][2] for c in chars]),
            char_attack=round(sum([c['attack'][2] for c in chars]), 1),
            repair=round(sum([c['repair'][2] for c in chars]), 1),
            immunity_date=immunity_date,
        )
        layout = self.psa.get_layout(rooms, ship)
        self.psa.calc_armor_effects(rooms, layout)
        items = sorted([
            dict(
                self.psa.item_map[int(x['@ItemDesignId'])],
                quantity=int(x['@Quantity']),
            )
            for x in ship_d['Items']['Item']
            if int(x['@Quantity']) > 0
        ], key=lambda x: (self.psa.item_type[x['type']], x['name']))
        upgrades = sorted(self.upgrades, key=itemgetter('amount'))
        return ship, user, chars, rooms, items, upgrades

    def get_char(self, x, ship_level, order):
        stats = self.psa.char_map[int(x['@CharacterDesignId'])].copy()
        items = self.get_char_items(x)
        level = int(x['@Level'])
        stamina = int(x['@StaminaImprovement'])
        progression_type = stats['progression_type']

        training = stamina
        for k, training_key in self.psa.stat_map.items():
            (start, end) = stats[k]
            improvement = int(x[training_key]) if training_key in x else 0
            training += improvement

            current = start
            if progression_type == 'Linear':
                current += (end - start) * ((level - 1) / 39)
            elif progression_type == 'EaseIn':
                current += (end - start) * ((level - 1) / 39) ** 2
            elif progression_type == 'EaseOut':
                current += (end - start) * ((level - 1) / 39) ** .5

            stats[k] = [start, end, current, improvement, 0]    # start, end, current, +% +

        stats['stamina'] = stamina

        # Item effects
        for part, i in items.items():
            e = i['enhancement']
            if e in self.psa.enhance_stats:
                stats[self.psa.enhance_stats[e]] += i['bonus']
            # elif e == 'science':    # Science was removed from chars, as was shield... 4/26/2018
            #     pass
            else:
                stats[e][4] += i.get('bonus', 0)

            extra = i['extra_enhancement']
            if extra in self.psa.enhance_stats:
                stats[self.psa.enhance_stats[extra]] += i['extra_bonus']
            elif extra:
                stats[extra][4] += i['extra_bonus']

        # Final calculations and rounding
        for s in self.psa.stat_map:
            train_scale = (1 + stats[s][3] / 100)

            if s == 'ability':
                item_scale = (1 + stats[s][4] / 100)
                item_add = 0
            else:
                item_scale = 1
                item_add = stats[s][4]

            stats[s][2] = stats[s][2] * train_scale * item_scale + item_add
            stats[s][1] = stats[s][1] * train_scale * item_scale + item_add

            for i in range(0, 5):
                if s == 'hp' and i == 2:
                    stats[s][i] = int(round(stats[s][i]))
                else:
                    stats[s][i] = round(stats[s][i], 1)

        stats['training'] = training
        stats['level'] = level
        stats['char_name'] = x['@CharacterName']
        stats['room_id'] = int(x['@RoomId'])
        stats['character_id'] = int(x['@CharacterId'])
        stats['xp'] = int(x['@Xp'])
        stats['order'] = order
        target_xp = self.psa.leg_level_xp[stats['level']] if ('legendary' == stats['rarity']) \
            else self.psa.level_xp[stats['level']]
        stats['upgradable'] = stats['xp'] >= target_xp and stats['level'] < min(ship_level * 4, 40)
        stats['equipment'] = dict(stats['equipment'], **items)
        stats['char_id'] = int(x['@CharacterId'])
        return stats

    def get_char_items(self, char_data):
        item_data = char_data['Items']
        if item_data:
            items = item_data['Item']
            if type(items) is not list:
                items = [items]

            item_list = [
                dict(
                    self.psa.item_map[int(i['@ItemDesignId'])],
                    extra_enhancement=i.get('@BonusEnhancementType', '').lower(),
                    extra_bonus=float(i.get('@BonusEnhancementValue', 0))
                )
                for i in items
            ]
            items = {i['slot']: i for i in item_list}
            return items
        return {}
