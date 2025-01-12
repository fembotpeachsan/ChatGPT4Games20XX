#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#ifdef _WIN32
#include <direct.h>
#define mkdir(path, mode) _mkdir(path)
#else
#include <unistd.h>
#endif

// Maximum filename length
#define MAX_FILENAME 256

// Structure to hold file metadata
typedef struct {
    char filename[MAX_FILENAME];
    unsigned int filesize;
} FileHeader;

// Function to write a single file into the output
int write_file_to_package(FILE *out, const char *filepath) {
    FILE *in = fopen(filepath, "rb");
    if (!in) {
        fprintf(stderr, "Error: Cannot open input file %s\n", filepath);
        return -1;
    }

    // Get file size
    fseek(in, 0, SEEK_END);
    long size = ftell(in);
    fseek(in, 0, SEEK_SET);

    if (size < 0) {
        fprintf(stderr, "Error: Cannot determine size of %s\n", filepath);
        fclose(in);
        return -1;
    }

    // Prepare header
    FileHeader header;
    memset(&header, 0, sizeof(FileHeader));
    strncpy(header.filename, filepath, MAX_FILENAME - 1);
    header.filesize = (unsigned int)size;

    // Write header
    if (fwrite(&header, sizeof(FileHeader), 1, out) != 1) {
        fprintf(stderr, "Error: Failed to write header for %s\n", filepath);
        fclose(in);
        return -1;
    }

    // Write file data
    char buffer[4096];
    size_t bytes;
    while ((bytes = fread(buffer, 1, sizeof(buffer), in)) > 0) {
        if (fwrite(buffer, 1, bytes, out) != bytes) {
            fprintf(stderr, "Error: Failed to write data for %s\n", filepath);
            fclose(in);
            return -1;
        }
    }

    fclose(in);
    return 0;
}

// Function to compile the N64 codebase into a .z64 file
int compile_codebase(const char *codebase_dir, const char *output_rom) {
    char command[1024];

    // Change directory to the codebase directory
    // Note: Changing directory within a C program affects only the current process
    if (chdir(codebase_dir) != 0) {
        fprintf(stderr, "Error: Cannot change directory to %s\n", codebase_dir);
        return -1;
    }

    // Example compilation command using libdragon's makefile
    // Adjust the command based on your specific build system
    snprintf(command, sizeof(command), "make clean && make");

    printf("Compiling codebase in %s...\n", codebase_dir);
    int ret = system(command);
    if (ret != 0) {
        fprintf(stderr, "Error: Compilation failed.\n");
        return -1;
    }

    // Assume the build system outputs a .z64 file named as per output_rom
    // You might need to adjust the path based on your build configuration
    // For example, libdragon outputs to /build/z64/yourgame.z64
    // Adjust accordingly
    // Here, we assume the makefile places the .z64 in the codebase_dir
    // You may need to specify the exact path
    // Example:
    // snprintf(command, sizeof(command), "cp build/z64/%s.z64 ../%s", output_rom, output_rom);
    // For simplicity, let's assume the .z64 is named output_rom and is in the codebase_dir

    // Verify that the .z64 file exists
    struct stat buffer_stat;
    if (stat(output_rom, &buffer_stat) != 0) {
        fprintf(stderr, "Error: Compiled .z64 file %s not found.\n", output_rom);
        return -1;
    }

    printf("Compilation successful. Generated ROM: %s\n", output_rom);
    return 0;
}

// Usage information
void print_usage(const char *progname) {
    printf("Usage: %s output_package.bin codebase_dir output_rom.z64 [input1 ... inputN]\n", progname);
    printf("\n");
    printf("Parameters:\n");
    printf("  output_package.bin   - Name of the output package file.\n");
    printf("  codebase_dir         - Directory containing the N64 codebase to compile.\n");
    printf("  output_rom.z64       - Name of the compiled .z64 ROM file.\n");
    printf("  input1 ... inputN    - Additional input files to include in the package.\n");
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    const char *output_package = argv[1];
    const char *codebase_dir = argv[2];
    const char *output_rom = argv[3];

    // Compile the codebase into a .z64 file
    if (compile_codebase(codebase_dir, output_rom) != 0) {
        fprintf(stderr, "Error: Failed to compile the codebase.\n");
        return EXIT_FAILURE;
    }

    // Create the output package
    FILE *out = fopen(output_package, "wb");
    if (!out) {
        fprintf(stderr, "Error: Cannot create output file %s\n", output_package);
        return EXIT_FAILURE;
    }

    // Write a simple package header (e.g., number of files)
    // +1 for the compiled ROM
    unsigned int file_count = (argc - 4) + 1;
    if (fwrite(&file_count, sizeof(unsigned int), 1, out) != 1) {
        fprintf(stderr, "Error: Failed to write package header.\n");
        fclose(out);
        return EXIT_FAILURE;
    }

    // First, add the compiled .z64 ROM
    if (write_file_to_package(out, output_rom) != 0) {
        fprintf(stderr, "Error: Failed to package ROM file %s\n", output_rom);
        fclose(out);
        return EXIT_FAILURE;
    }
    printf("Packaged ROM: %s\n", output_rom);

    // Process additional input files
    for (int i = 4; i < argc; ++i) {
        if (write_file_to_package(out, argv[i]) != 0) {
            fprintf(stderr, "Error: Failed to package file %s\n", argv[i]);
            fclose(out);
            return EXIT_FAILURE;
        }
        printf("Packaged: %s\n", argv[i]);
    }

    fclose(out);
    printf("Package created successfully: %s\n", output_package);
    return EXIT_SUCCESS;
}
