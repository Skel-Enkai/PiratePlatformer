# this code sucks, and is not needed. For multiplayer will need to identify different controllers better.
# However, no plans for multiplayer anyway.

def joysticks_add(joysticks):
    current = []
    for joystick in joysticks:
        current.append(joystick.get_id())
    print(current)
    current.sort()
    if current:
        for index, item in enumerate(current):
            if index != item:
                return joysticks.append(pygame.joystick.Joystick(index))
        return joysticks.append(pygame.joystick.Joystick(len(current)))
    else:
        return joysticks.append(pygame.joystick.Joystick(0))


def joysticks_remove(joysticks, id):
    for joystick in joysticks:
        if joystick.get_instance_id() == id:
            return joysticks.remove(joystick)
