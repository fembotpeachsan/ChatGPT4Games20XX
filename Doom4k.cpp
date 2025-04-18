#include <SDL2/SDL.h>
#include <cmath>
#include <iostream>

#define SCREEN_WIDTH 640
#define SCREEN_HEIGHT 480
#define MAP_WIDTH 5
#define MAP_HEIGHT 5
#define FOV (M_PI / 3.0) // 60 degrees field of view
#define MOVE_SPEED 0.1
#define ROT_SPEED 0.05

// Simple 2D map: 1 = wall, 0 = empty space
int map[MAP_HEIGHT][MAP_WIDTH] = {
    {1, 1, 1, 1, 1},
    {1, 0, 0, 0, 1},
    {1, 0, 1, 0, 1},
    {1, 0, 0, 0, 1},
    {1, 1, 1, 1, 1}
};

// Player variables
float playerX = 1.5f;
float playerY = 1.5f;
float playerAngle = 0.0f;

void render(SDL_Renderer* renderer) {
    // Clear screen with floor and ceiling
    SDL_SetRenderDrawColor(renderer, 100, 100, 100, 255); // Ceiling (gray)
    SDL_Rect ceiling = {0, 0, SCREEN_WIDTH, SCREEN_HEIGHT / 2};
    SDL_RenderFillRect(renderer, &ceiling);

    SDL_SetRenderDrawColor(renderer, 50, 50, 50, 255); // Floor (darker gray)
    SDL_Rect floor = {0, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT / 2};
    SDL_RenderFillRect(renderer, &floor);

    // Raycasting
    for (int x = 0; x < SCREEN_WIDTH; x++) {
        float rayAngle = playerAngle - FOV / 2.0f + (float)x / SCREEN_WIDTH * FOV;
        float rayDirX = cos(rayAngle);
        float rayDirY = sin(rayAngle);

        int mapX = (int)playerX;
        int mapY = (int)playerY;

        float sideDistX, sideDistY;
        float deltaDistX = (rayDirX == 0) ? 1e30 : fabs(1.0f / rayDirX);
        float deltaDistY = (rayDirY == 0) ? 1e30 : fabs(1.0f / rayDirY);

        int stepX, stepY;
        if (rayDirX < 0) {
            stepX = -1;
            sideDistX = (playerX - mapX) * deltaDistX;
        } else {
            stepX = 1;
            sideDistX = (mapX + 1.0f - playerX) * deltaDistX;
        }
        if (rayDirY < 0) {
            stepY = -1;
            sideDistY = (playerY - mapY) * deltaDistY;
        } else {
            stepY = 1;
            sideDistY = (mapY + 1.0f - playerY) * deltaDistY;
        }

        bool hit = false;
        int side; // 0 = x-side, 1 = y-side
        float perpWallDist;

        // DDA algorithm
        while (!hit) {
            if (sideDistX < sideDistY) {
                sideDistX += deltaDistX;
                mapX += stepX;
                side = 0;
            } else {
                sideDistY += deltaDistY;
                mapY += stepY;
                side = 1;
            }
            if (map[mapY][mapX] > 0) hit = true;
        }

        // Calculate perpendicular distance to avoid fisheye effect
        if (side == 0) perpWallDist = (mapX - playerX + (1 - stepX) / 2.0f) / rayDirX;
        else perpWallDist = (mapY - playerY + (1 - stepY) / 2.0f) / rayDirY;

        // Calculate wall height
        int lineHeight = (int)(SCREEN_HEIGHT / perpWallDist);
        int drawStart = -lineHeight / 2 + SCREEN_HEIGHT / 2;
        if (drawStart < 0) drawStart = 0;
        int drawEnd = lineHeight / 2 + SCREEN_HEIGHT / 2;
        if (drawEnd >= SCREEN_HEIGHT) drawEnd = SCREEN_HEIGHT - 1;

        // Set wall color (brighter for x-sides, darker for y-sides)
        if (side == 0) SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255); // White
        else SDL_SetRenderDrawColor(renderer, 128, 128, 128, 255); // Gray

        // Draw vertical line
        SDL_RenderDrawLine(renderer, x, drawStart, x, drawEnd);
    }
}

void handleInput(bool& running) {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) running = false;
        if (event.type == SDL_KEYDOWN) {
            float dirX = cos(playerAngle);
            float dirY = sin(playerAngle);
            switch (event.key.keysym.sym) {
                case SDLK_w: // Move forward
                    if (map[(int)(playerY + dirY * MOVE_SPEED)][(int)(playerX + dirX * MOVE_SPEED)] == 0) {
                        playerX += dirX * MOVE_SPEED;
                        playerY += dirY * MOVE_SPEED;
                    }
                    break;
                case SDLK_s: // Move backward
                    if (map[(int)(playerY - dirY * MOVE_SPEED)][(int)(playerX - dirX * MOVE_SPEED)] == 0) {
                        playerX -= dirX * MOVE_SPEED;
                        playerY -= dirY * MOVE_SPEED;
                    }
                    break;
                case SDLK_a: // Turn left
                    playerAngle -= ROT_SPEED;
                    if (playerAngle < 0) playerAngle += 2 * M_PI;
                    break;
                case SDLK_d: // Turn right
                    playerAngle += ROT_SPEED;
                    if (playerAngle >= 2 * M_PI) playerAngle -= 2 * M_PI;
                    break;
            }
        }
    }
}

int main(int argc, char* args[]) {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        std::cerr << "SDL could not initialize! SDL_Error: " << SDL_GetError() << std::endl;
        return 1;
    }

    SDL_Window* window = SDL_CreateWindow("Doom Raycasting", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_SHOWN);
    if (!window) {
        std::cerr << "Window could not be created! SDL_Error: " << SDL_GetError() << std::endl;
        SDL_Quit();
        return 1;
    }

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        std::cerr << "Renderer could not be created! SDL_Error: " << SDL_GetError() << std::endl;
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    bool running = true;
    while (running) {
        handleInput(running);
        render(renderer);
        SDL_RenderPresent(renderer);
    }

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
