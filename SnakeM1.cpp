#include <SDL2/SDL.h>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <iostream>

// Game constants
const int SCREEN_WIDTH  = 800;
const int SCREEN_HEIGHT = 600;
const int CELL_SIZE     = 20;                 // Each grid cell is 20x20 pixels
const int FPS           = 60;
const int FRAME_DELAY   = 1000 / FPS;         // Milliseconds per frame
const int MOVE_INTERVAL = 150;                // Milliseconds between snake moves

// Direction enumeration for snake movement
enum Direction { UP, DOWN, LEFT, RIGHT };

int main(int argc, char* argv[]) {
    // Initialize SDL2 video
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        std::cout << "SDL could not initialize! Error: " << SDL_GetError() << "\n";
        return 1;
    }

    // Create the SDL window
    SDL_Window* window = SDL_CreateWindow("Snake Game",
                                          SDL_WINDOWPOS_CENTERED,
                                          SDL_WINDOWPOS_CENTERED,
                                          SCREEN_WIDTH,
                                          SCREEN_HEIGHT,
                                          SDL_WINDOW_SHOWN);
    if (!window) {
        std::cout << "Window could not be created! Error: " << SDL_GetError() << "\n";
        SDL_Quit();
        return 1;
    }

    // Create the SDL renderer
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        std::cout << "Renderer could not be created! Error: " << SDL_GetError() << "\n";
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // Initialize random seed and game state
    std::srand(static_cast<unsigned int>(std::time(nullptr)));
    std::vector<SDL_Point> snake;
    // Calculate grid dimensions
    int cols = SCREEN_WIDTH / CELL_SIZE;
    int rows = SCREEN_HEIGHT / CELL_SIZE;
    // Start the snake in the middle of the grid
    snake.push_back({ cols / 2, rows / 2 });
    Direction dir = RIGHT;

    // Lambda to spawn food in a random grid cell not occupied by the snake
    auto spawnFood = [&snake, cols, rows]() -> SDL_Point {
        SDL_Point food;
        bool valid = false;
        while (!valid) {
            food.x = std::rand() % cols;
            food.y = std::rand() % rows;
            valid = true;
            // Ensure food is not on the snake
            for (const auto& segment : snake) {
                if (segment.x == food.x && segment.y == food.y) {
                    valid = false;
                    break;
                }
            }
        }
        return food;
    };

    SDL_Point food = spawnFood();

    bool quit = false;
    SDL_Event event;
    Uint32 lastMoveTime = SDL_GetTicks();

    // Main game loop
    while (!quit) {
        Uint32 frameStart = SDL_GetTicks();
        // --- Event Handling ---
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                quit = true;
            }
            if (event.type == SDL_KEYDOWN) {
                switch (event.key.keysym.sym) {
                    case SDLK_UP:
                        if (dir != DOWN) dir = UP;
                        break;
                    case SDLK_DOWN:
                        if (dir != UP) dir = DOWN;
                        break;
                    case SDLK_LEFT:
                        if (dir != RIGHT) dir = LEFT;
                        break;
                    case SDLK_RIGHT:
                        if (dir != LEFT) dir = RIGHT;
                        break;
                    case SDLK_ESCAPE:
                        quit = true;
                        break;
                    default:
                        break;
                }
            }
        }

        // --- Game Update (based on MOVE_INTERVAL) ---
        Uint32 currentTime = SDL_GetTicks();
        if (currentTime - lastMoveTime >= MOVE_INTERVAL) {
            lastMoveTime = currentTime;
            // Determine the new head position
            SDL_Point newHead = snake.front();
            switch (dir) {
                case UP:    newHead.y -= 1; break;
                case DOWN:  newHead.y += 1; break;
                case LEFT:  newHead.x -= 1; break;
                case RIGHT: newHead.x += 1; break;
            }

            // Check for collision with walls
            if (newHead.x < 0 || newHead.x >= cols || newHead.y < 0 || newHead.y >= rows) {
                // Collision detected – reset the game
                snake.clear();
                snake.push_back({ cols / 2, rows / 2 });
                dir = RIGHT;
                food = spawnFood();
                continue;
            }

            // Check for collision with itself
            bool collision = false;
            for (const auto& segment : snake) {
                if (newHead.x == segment.x && newHead.y == segment.y) {
                    collision = true;
                    break;
                }
            }
            if (collision) {
                // Collision detected – reset the game
                snake.clear();
                snake.push_back({ cols / 2, rows / 2 });
                dir = RIGHT;
                food = spawnFood();
                continue;
            }

            // Move the snake: insert the new head at the front
            snake.insert(snake.begin(), newHead);

            // Check if the snake has eaten the food
            if (newHead.x == food.x && newHead.y == food.y) {
                // Food eaten – spawn new food (do not remove the tail, so the snake grows)
                food = spawnFood();
            } else {
                // Normal move – remove the tail segment
                snake.pop_back();
            }
        }

        // --- Rendering ---
        // Clear the screen with a black background
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);

        // Draw the food as a red square
        SDL_Rect foodRect = { food.x * CELL_SIZE, food.y * CELL_SIZE, CELL_SIZE, CELL_SIZE };
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
        SDL_RenderFillRect(renderer, &foodRect);

        // Draw the snake as a series of green squares
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255);
        for (const auto& segment : snake) {
            SDL_Rect rect = { segment.x * CELL_SIZE, segment.y * CELL_SIZE, CELL_SIZE, CELL_SIZE };
            SDL_RenderFillRect(renderer, &rect);
        }

        // Present the rendered frame on the screen
        SDL_RenderPresent(renderer);

        // --- Frame Rate Control ---
        Uint32 frameTime = SDL_GetTicks() - frameStart;
        if (frameTime < FRAME_DELAY) {
            SDL_Delay(FRAME_DELAY - frameTime);
        }
    }

    // Cleanup and shutdown
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}
