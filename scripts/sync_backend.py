
import shutil
import os

# Define paths
root_dir = "/Users/yaksheng/projects/cactus-hackathon-cluely"
backend_src = os.path.join(root_dir, "app/backend")
frontend_backend_dst = os.path.join(root_dir, "app/frontend/python_backend")

main_src = os.path.join(root_dir, "src/main.py")
frontend_main_dst = os.path.join(root_dir, "app/frontend/src/main.py")

print(f"Syncing python backend code...")

# 1. Sync server.py
print(f"Copying {os.path.join(backend_src, 'server.py')} -> {os.path.join(frontend_backend_dst, 'server.py')}")
shutil.copy2(os.path.join(backend_src, "server.py"), os.path.join(frontend_backend_dst, "server.py"))

# 2. Sync notion_tools
print(f"Copying {os.path.join(backend_src, 'notion_tools')} -> {os.path.join(frontend_backend_dst, 'notion_tools')}")
if os.path.exists(os.path.join(frontend_backend_dst, "notion_tools")):
    shutil.rmtree(os.path.join(frontend_backend_dst, "notion_tools"))
shutil.copytree(os.path.join(backend_src, "notion_tools"), os.path.join(frontend_backend_dst, "notion_tools"))

# 3. Sync slack_tools
print(f"Copying {os.path.join(backend_src, 'slack_tools')} -> {os.path.join(frontend_backend_dst, 'slack_tools')}")
if os.path.exists(os.path.join(frontend_backend_dst, "slack_tools")):
    shutil.rmtree(os.path.join(frontend_backend_dst, "slack_tools"))
shutil.copytree(os.path.join(backend_src, "slack_tools"), os.path.join(frontend_backend_dst, "slack_tools"))

# 4. Sync main.py
print(f"Copying {main_src} -> {frontend_main_dst}")
shutil.copy2(main_src, frontend_main_dst)

# 5. Sync cactus folder (code and weights)
cactus_src = os.path.join(root_dir, "cactus")
frontend_cactus_dst = os.path.join(root_dir, "app/frontend/cactus")

print(f"Syncing cactus folder (this may take a while)...")
if os.path.exists(frontend_cactus_dst):
    shutil.rmtree(frontend_cactus_dst)

# Copy python src
shutil.copytree(os.path.join(cactus_src, "python/src"), os.path.join(frontend_cactus_dst, "python/src"))

# Copy the compiled library (libcactus.dylib/so)
# Source: cactus/cactus/build
# Dest: app/frontend/cactus/cactus/build (to match relative path in cactus.py)
lib_src = os.path.join(cactus_src, "cactus", "build")
lib_dst = os.path.join(frontend_cactus_dst, "cactus", "build")

print(f"Copying compiled library from {lib_src} -> {lib_dst}")
if os.path.exists(lib_src):
    # Ensure parent dir exists (app/frontend/cactus/cactus)
    os.makedirs(os.path.dirname(lib_dst), exist_ok=True)
    if os.path.exists(lib_dst):
        shutil.rmtree(lib_dst)
    shutil.copytree(lib_src, lib_dst)
else:
    print(f"Warning: {lib_src} not found! The app will fail to load the model.")

# Copy weights (only functiongemma and whisper to save space/time if needed, but copying all for safety)
# If copying all takes too long, we can selectively copy.
# For now, let's copy specific weights to avoid huge copy times if there are many models.
os.makedirs(os.path.join(frontend_cactus_dst, "weights"), exist_ok=True)

models_to_copy = ["functiongemma-270m-it", "whisper-small", "lfm2-vl-450m"]
for model in models_to_copy:
    src_path = os.path.join(cactus_src, "weights", model)
    dst_path = os.path.join(frontend_cactus_dst, "weights", model)
    if os.path.exists(src_path):
        print(f"Copying {model}...")
        shutil.copytree(src_path, dst_path)
    else:
        print(f"Warning: Model {model} not found in source weights.")

print("Sync complete.")
