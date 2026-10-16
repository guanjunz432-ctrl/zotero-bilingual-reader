"""Bounded, ephemeral Codex CLI requests; no ACP sessions or credential copies."""
from __future__ import annotations
import json, subprocess, tempfile, time
from settings import load_settings, cloud_environment
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

class TranslationServiceError(RuntimeError):
    """A document-wide failure: do not retry it separately for every page."""
    fatal = True

def settings():
    result = dict(model='gpt-6-luna', vision_model='gpt-6.1-sol', reasoning_effort='low', timeout_seconds=240, max_attempts=2)
    path = ROOT/'translation-settings.json'
    if path.exists():
        result.update(json.loads(path.read_text(encoding='utf-8-sig')))
    result.update(load_settings().get('translation', {}))
    if result['reasoning_effort'] not in ('low', 'medium', 'high'):
        raise ValueError('翻译推理强度仅支持 low、medium、high')
    if any(not isinstance(result[k], str) or not result[k].strip() for k in ('model','vision_model')):
        raise ValueError('翻译模型不能为空')
    result['timeout_seconds'] = max(30, min(600, int(result['timeout_seconds'])))
    result['max_attempts'] = max(1, min(3, int(result['max_attempts'])))
    return result

def find_codex():
    executable = Path(load_settings()['codex_path'])
    if not executable.is_file():
        raise TranslationServiceError('找不到插件的官方 Codex CLI；请重新运行 setup.ps1。')
    return str(executable)

class CodexTranslation:
    def __init__(self, cwd):
        self.cwd = Path(cwd)
        self.env = cloud_environment(load_settings())
        self.config = settings()
        self.codex = find_codex()
        self.last_metadata = {}

    def command(self, image, output):
        command = [self.codex, 'exec', '--ephemeral', '--ignore-user-config',
                   '--skip-git-repo-check', '--sandbox', 'read-only', '--json',
                   '--model', self.config['model'], '--output-last-message', str(output)]
        overrides = {
            'model_reasoning_effort': self.config['reasoning_effort'],
            'model_instructions_file': str(ROOT/'translation-instructions.txt'),
            'project_doc_max_bytes': 0,
            'web_search': 'disabled',
            'features.shell_tool': False,
            'features.unified_exec': False,
            'features.multi_agent': False,
            'features.plugins': False,
            'features.memories': False,
            'features.hooks': False,
            'features.skip_host_skill_discovery': True,
            'features.respect_system_proxy': True,
        }
        for key, value in overrides.items():
            command += ['-c', key+'='+json.dumps(value, ensure_ascii=False)]
        if image is not None:
            command += ['--image', str(image)]
        return command+['-']

    def request(self, prompt, image=None):
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix='translation-', dir=self.cwd) as tmp:
            output = Path(tmp)/'final.json'
            try:
                result = subprocess.run(self.command(image, output), input=prompt,
                    cwd=self.cwd, env=self.env, text=True, encoding='utf-8', errors='replace',
                    capture_output=True, timeout=self.config['timeout_seconds'],
                    creationflags=NO_WINDOW)
            except subprocess.TimeoutExpired as exc:
                raise TimeoutError('本页云端请求超时；已完成译文保留。') from exc
            usage, error, thread_id, tools_used = {}, '', None, []
            # Keep only final-answer metadata. Never persist reasoning, tool
            # arguments, the raw event stream, environment or authentication.
            for line in result.stdout.splitlines():
                try: event = json.loads(line)
                except ValueError: continue
                if event.get('type') == 'thread.started':
                    thread_id = event.get('thread_id')
                if event.get('type') == 'turn.completed':
                    usage = event.get('usage', {})
                if event.get('type') in ('error', 'turn.failed'):
                    detail = event.get('error', event)
                    if isinstance(detail, dict): error = str(detail.get('message', ''))
                if event.get('type') == 'item.completed':
                    kind = event.get('item', {}).get('type')
                    if kind in ('command_execution', 'mcp_tool_call', 'web_search', 'file_change'):
                        tools_used.append(kind)
            self.last_metadata = dict(model=self.config['model'],
                reasoning_effort=self.config['reasoning_effort'], ephemeral=True,
                elapsed_seconds=round(time.monotonic()-started, 2), usage=usage,
                thread_id=thread_id, tools_used=tools_used)
            if result.returncode or error or not output.exists():
                detail = error.lower()
                if any(s in detail for s in ('usage limit', 'rate limit', 'quota', 'credits')):
                    raise TranslationServiceError('Codex 额度或速率受限；已停止本篇，稍后从缓存续传。')
                if any(s in detail for s in ('auth', 'login', 'unauthorized', '401')):
                    raise TranslationServiceError('Codex 登录不可用；请运行 login.ps1 重新登录后续传。')
                if any(s in detail for s in ('model', 'not supported', 'not found')):
                    raise TranslationServiceError('所选翻译模型或参数不可用；请检查模型设置或账户的模型权限。')
                # Do not echo arbitrary stderr, which may include private data.
                raise TranslationServiceError(f'Codex 翻译进程失败（{result.returncode}）；请先检查官方 Codex 连接与版本。')
            raw = output.read_text(encoding='utf-8').strip()
            if not raw:
                raise RuntimeError('云端返回空译文')
            if tools_used:
                raise TranslationServiceError('翻译请求意外调用工具，结果已拒绝。')
            return raw

    def close(self):
        pass
