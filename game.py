import time

from kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment
# from KeyboardController import KeyboardController
from test_controller import TestController
from actions.dodge import DodgeAgent

def main(print_flag: bool = False):
    
    global perf_data, score
    my_test_scenario = Scenario(
        name="Test Scenario",
        # num_asteroids=10,
        asteroid_states=[
        {"position": (700, 501), "speed": 100, "angle": -180, "size": 4},
        {"position": (400, 501), "speed": 100, "angle": -180, "size": 4},
        {"position": (200, 510), "speed": 100, "angle": 0, "size": 4},
        {"position": (450, 200), "speed": 100, "angle": 45, "size": 4},
        {"position": (0, 510), "speed": -100, "angle": 45, "size": 4},
        ],
        ship_states=[
            {"position": (500, 500), "angle": 180, "lives": 999, "team": 4},
        ],
        map_size=(1000, 800),
        time_limit=99,
        ammo_limit_multiplier=0,
        stop_if_no_ammo=False,
    )

    game_settings = {
        "perf_tracker": True,
        "graphics_type": GraphicsType.Tkinter,
        "realtime_multiplier": -1,
        "graphics_obj": None,
    }
    # Use this to visualize the game scenario


    game = KesslerGame(settings=game_settings)
    # game = TrainerEnvironment(settings=game_settings)  # Use this for max-speed, no-graphics simulation

    pre = time.perf_counter()
    score, perf_data = game.run(
        scenario=my_test_scenario, controllers=[TestController()]
        # scenario=my_test_scenario, controllers=[KeyboardController()]
        )
    
    # print(perf_data)

    if (print_flag):
        print("Scenario eval time: " + str(time.perf_counter() - pre))
        print(score.stop_reason)
        print("Asteroids hit: " + str([team.asteroids_hit for team in score.teams]))
        print("Deaths: " + str([team.deaths for team in score.teams]))
        print("Accuracy: " + str([team.accuracy for team in score.teams]))
        print("Mean eval time: " + str([team.mean_eval_time for team in score.teams]))
        print(
            "Evaluated frames: "
            + str([controller.eval_frames for controller in score.final_controllers])
        )
    
if __name__ == '__main__':
    # episode = 100

    # # # Training for Dodge Actor Critic
    # for i in range(episode):
    #     e_reward = 0
        
    #     main()
    #     agent = DodgeAgent()
        
    #     for team in score.teams:
    #         if team.deaths > 0:
    #             # Penalize for each death
    #             e_reward -= 50 * team.deaths
    #         elif team.deaths <= 0:
    #             # Reward for survival
    #             if team.deaths > 0:
    #                 e_reward += 50 * score.lives
                    
    #     action = agent.actor.suggest_action(agent.random_var[2])
            
    #     # Critic evaluates action
    #     action_value = agent.critic.evaluate(action)
        
    #     # Update episode reward based on action value
    #     e_reward += action_value
        
        
    #     agent.update_var(e_reward)
    #     print(e_reward)
    main()
        
