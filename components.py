import random


class Dice:
    def __init__(self, size=6):
        self.size = size
        self.rolls = list()

    def roll(self):
        roll = random.randint(1, self.size)
        self.rolls += [roll]
        return roll


class BoardComponent:
    def __init__(self, output_pos):
        self.output_pos = output_pos


class Snake(BoardComponent):
    """Moves a player down the board"""

    def __init__(self, output_pos):
        super().__init__(output_pos)


class Ladder(BoardComponent):
    """Moves a player up the board"""

    def __init__(self, output_pos):
        super().__init__(output_pos)


class Player:
    def __init__(self, name):
        self.name = name

        # init counters
        self._snake_hits = 0
        self._snake_distance = 0
        self._ladder_hits = 0
        self._ladder_distance = 0
        self._regular_moves = 0
        self._turns = 0
        self._current_pos = None
        self.has_won = False

    def move_player_to(self, move_to, how):
        diff = move_to - self._current_pos
        self._current_pos = move_to
        if how == "snake":
            self._snake_hits += 1
            self._snake_distance += diff
        elif how == "ladder":
            self._ladder_hits += 1
            self._ladder_distance += diff
        else:
            self._regular_moves += diff
            self._turns += 1

    def print_details(self):
        if self.has_won:
            print("-!-!- WINNER --", self.name.title(), "Details -- WINNER -!-!-")
        else:
            print("-----", self.name.title(), "Details -----")
        print("\t Ladders:", self._ladder_distance, "in", self._ladder_hits, "climbs")
        print("\t Snakes:", self._snake_distance, "in", self._snake_hits, "slides")
        print("\t Regular moves:", self._regular_moves, "in", self._turns, "turns")
        print()

    def get_pos(self):
        return self._current_pos


class PlayerSet:
    def __init__(self, player_names: list):
        self.player_names = player_names

        # set -> list jumbles the players
        players = set()
        for name in self.player_names:
            player = Player(name)
            players.add(player)

        self.player_list = list(players)
        self._len = len(players)

        self._total_turns = 0

    def __next__(self):
        # this dosent matter were starting on pos 1
        self._total_turns += 1
        return self.player_list[self._total_turns % self._len]

    def initialize_players(self, initial_pos=0):
        for player in self.player_list:
            player._current_pos = initial_pos


class Board:
    def __init__(self, player_names: list, length: int = 50, num_snakes: int = 5, num_ladders: int = 5) -> None:
        self.players = PlayerSet(player_names)
        self.board_len = length
        self.component_positions = [None for _ in range(self.board_len)]
        self.num_snakes = num_snakes
        self.num_ladders = num_ladders

        # init internal items
        self.snakes = list()
        self.ladders = list()

        self._construct_board()
        self._print_components()
        print("Board constructed")

    def _construct_board(self):
        # Ladders First
        print()
        for _ in range(self.num_ladders):
            # first & last 5% of the board shouldn't contain any ladders
            start_pos = random.randint(int(0.05 * self.board_len), int(0.95 * self.board_len))
            while self._position_filled(start_pos):
                # if the position is filled, try again
                start_pos = random.randint(int(0.05 * self.board_len), int(0.95 * self.board_len))

            # end positions go up the board to the end
            end_pos = random.randint(start_pos, self.board_len-1)

            ladder = Ladder(end_pos)
            # Add the ladder to the board details
            self.component_positions[start_pos] = ladder
            self.ladders.append(ladder)

        # Then Snakes
        for _ in range(self.num_snakes):
            # first 10% of the board should be empty of snake heads
            head_pos = random.randint(int(0.1 * self.board_len), self.board_len-1)
            while self._position_filled(head_pos):
                head_pos = random.randint(int(0.1 * self.board_len), self.board_len-1)

            # End pos should be between the start and the head position
            end_pos = random.randint(0, head_pos)

            snake = Snake(end_pos)
            # Add the snakes to the board details
            self.component_positions[head_pos] = snake
            self.snakes.append(snake)

        # Create the dice for the board
        self.dice = Dice()

        # finally place all the players on position 0
        self.players.initialize_players(0)

    def _print_components(self):
        for index, component in enumerate(self.component_positions):
            if component is not None:
                print(type(component).__name__, "at", index, "leads to", component.output_pos)

    def _position_filled(self, pos_to_check):
        return self.component_positions[pos_to_check] is not None

    def play_auto(self):
        current_player = self.players.__next__()
        while not current_player.has_won:
            dice_roll = self.dice.roll()
            print()
            print(current_player.name.title() + "s turn.")
            print("Currently at", current_player.get_pos(), "and rolled a", dice_roll)

            new_board_index = current_player.get_pos() + dice_roll
            if new_board_index >= self.board_len:
                current_player.has_won = True
                print(current_player.name, "has won!!!!")
                break
            else:
                landed_pos = self.component_positions[new_board_index]

                if self._position_filled(new_board_index):
                    if type(landed_pos) == Snake:
                        print("\tIts a snake!\t Moving player from position", new_board_index, "to",
                              landed_pos.output_pos)
                        current_player.move_player_to(landed_pos.output_pos, "snake")
                    elif type(landed_pos) == Ladder:
                        print("\tIts a Ladder!\t Moving player from position", new_board_index, "to",
                              landed_pos.output_pos)
                        current_player.move_player_to(landed_pos.output_pos, "ladder")
                        if current_player.get_pos() >= self.board_len:
                            current_player.has_won = True
                            print(current_player.name, "has won!!!!")
                            break
                else:
                    # position is free, move them there
                    print("\tMoving player from position", current_player.get_pos(), "to",
                          new_board_index)
                    current_player.move_player_to(new_board_index, "reg")

                current_player = self.players.__next__()

        for player in self.players.player_list:
            player.print_details()
