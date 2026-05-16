import re
with open("src/layouts/AdminLayout.vue", "r", encoding="utf-8") as f:
    c = f.read()

# Add platforms translations to zh
old_zh = "config: 'API配置', back: '返回聊天' }"
new_zh = "config: 'API配置', platforms: '平台管理', platConfig: '凭证配置', platReview: '待审核消息', platStats: '自动回复统计', back: '返回聊天' }"
c = c.replace(old_zh, new_zh)

# Add platforms translations to en
old_en = "config: 'API Config', back: 'Back to Chat' }"
new_en = "config: 'API Config', platforms: 'Platforms', platConfig: 'API Credentials', platReview: 'Review Queue', platStats: 'Reply Stats', back: 'Back to Chat' }"
c = c.replace(old_en, new_en)

print("Trans added")

# Add pendingCount variable after lang declarations
old_val = "const route = useRoute()"
new_val = """const route = useRoute()

const pendingCount = ref(0)
const fetchPending = async () => {
  try { const r = await fetch('/api/platforms/review?limit=1'); const d = await r.json(); pendingCount.value = d.length } catch {}
}
fetchPending()
setInterval(fetchPending, 30000)"""
c = c.replace(old_val, new_val)

# Add ref import
old_imp = "import { ref, watch, computed, reactive } from 'vue'"
if old_imp not in c:
    old_imp = "import { watch, computed, reactive } from 'vue'"
    c = c.replace(old_imp, "import { ref, watch, computed, reactive } from 'vue'")

# Add Connection icon import  
old_icons = "import { useRoute } from 'vue-router'"
new_icons = """import { useRoute } from 'vue-router'
import { Connection, DataAnalysis, Collection, ChatDotRound, Shop, Setting } from '@element-plus/icons-vue'"""
if 'Connection' not in c:
    # Find the imports section and add Connection
    old_icon_line = "DataAnalysis, Collection, ChatDotRound, Shop, Setting"
    if old_icon_line in c:
        c = c.replace(old_icon_line, "Connection, DataAnalysis, Collection, ChatDotRound, Shop, Setting")

with open("src/layouts/AdminLayout.vue", "w", encoding="utf-8") as f:
    f.write(c)
print("All done")
