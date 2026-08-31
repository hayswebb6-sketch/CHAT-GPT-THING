import random
import time


def game():
    print("================================")
    print("       THE DUNGEON OF CHAOS")
    print("================================")
    print("You wake up in a mysterious dungeon.")
    print("A sign says: 'Make good choices.'")

    health = 100
    gold = 10
    room = 1

    while health > 0:
        print(f"\n--- Room {room} ---")
        print(f"Health: {health} | Gold: {gold}")
        print("1. Open the door")
        print("2. Search the room")
        print("3. Run away")

        choice = input("> ").strip()

        if choice == "1":
            event = random.choice(["monster", "treasure", "trap", "empty"])

            if event == "monster":
                damage = random.randint(10, 30)
                print(f"A monster attacks you! You lose {damage} HP.")
                health -= damage
            elif event == "treasure":
                found = random.randint(5, 40)
                gold += found
                print(f"You found {found} gold!")
            elif event == "trap":
                damage = random.randint(5, 20)
                print(f"It's a trap! You lose {damage} HP.")
                health -= damage
            else:
                print("...Nothing happens. Suspicious.")

            room += 1

        elif choice == "2":
            if random.randint(1, 3) == 1:
                found = random.randint(1, 20)
                gold += found
                print(f"You found {found} gold under a rock!")
            else:
                print("You search everywhere and find absolutely nothing.")

        elif choice == "3":
            print("You sprint back toward the entrance...")
            time.sleep(1)
            print("You escaped the dungeon!")
            break

        else:
            print("That isn't a choice. The dungeon judges you silently.")

    if health <= 0:
        print("\nYOU DIED 💀")
    else:
        print(f"\nYou survived with {health} HP and {gold} gold!")


if __name__ == "__main__":
    game()
