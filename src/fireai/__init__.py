 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/src/fireai/__init__.py b/src/fireai/__init__.py
new file mode 100644
index 0000000000000000000000000000000000000000..66941d4c242397a97f6631d567383754751e9386
--- /dev/null
+++ b/src/fireai/__init__.py
@@ -0,0 +1,4 @@
+from fireai.scenario_loader import load_scenarios
+from fireai.session import FireAISession
+
+__all__ = ["load_scenarios", "FireAISession"]
 
EOF
)
