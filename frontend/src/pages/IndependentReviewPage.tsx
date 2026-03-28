/**
 * Independent Review Page — 独立改稿审稿工作台
 * 
 * 支持文本粘贴 / DOCX 上传两种输入，default / custom 两种规则模式
 */

import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, CardFooter, Button, Textarea, Input, Badge, Spinner } from '../components/ui';
import {
  reviewText,
  reviewDocx,
  type IndependentReviewResponse,
  type ReviewFinding,
  type ReviewRewriteTarget,
} from '../api/independent-review';
import { FileText, Upload, ArrowLeft, CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

type InputMode = 'text' | 'docx';
type RuleMode = 'default' | 'custom';

const SEVERITY_CONFIG: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  low: { icon: Info, color: 'text-blue-500', label: '建议' },
  medium: { icon: AlertTriangle, color: 'text-amber-500', label: '中等' },
  high: { icon: XCircle, color: 'text-orange-600', label: '严重' },
  critical: { icon: XCircle, color: 'text-red-600', label: '致命' },
};

export function IndependentReviewPage() {
  const navigate = useNavigate();
  
  // Input state
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const [ruleMode, setRuleMode] = useState<RuleMode>('default');
  const [content, setContent] = useState('');
  const [audience, setAudience] = useState('');
  const [customRules, setCustomRules] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Review state
  const [reviewing, setReviewing] = useState(false);
  const [result, setResult] = useState<IndependentReviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = inputMode === 'text'
    ? content.trim().length > 0
    : selectedFile !== null;

  async function handleSubmit() {
    if (!canSubmit) return;
    setReviewing(true);
    setError(null);
    setResult(null);

    try {
      let response: IndependentReviewResponse;
      if (inputMode === 'text') {
        response = await reviewText({
          content,
          audience: audience || undefined,
          rule_mode: ruleMode,
          custom_rules: ruleMode === 'custom' && customRules.trim()
            ? customRules.split('\n').filter(r => r.trim())
            : undefined,
        });
      } else {
        response = await reviewDocx(selectedFile!, {
          audience: audience || undefined,
          rule_mode: ruleMode,
          custom_rules: ruleMode === 'custom' ? customRules : undefined,
        });
      }
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : '审改失败');
    } finally {
      setReviewing(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">独立改稿审稿</h2>
          <p className="text-sm text-slate-500 mt-1">输入文本或上传 DOCX，使用规则引擎+大模型进行审改</p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
          <ArrowLeft size={16} /> 返回工作台
        </Button>
      </div>

      {/* Input Area */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <h3 className="text-sm font-semibold text-slate-800">输入内容</h3>
            <div className="flex rounded-md overflow-hidden border border-slate-200">
              <button
                className={`px-3 py-1 text-xs font-medium transition-colors ${
                  inputMode === 'text' ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
                }`}
                onClick={() => setInputMode('text')}
              >
                <FileText size={12} className="inline mr-1" /> 文本粘贴
              </button>
              <button
                className={`px-3 py-1 text-xs font-medium transition-colors ${
                  inputMode === 'docx' ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
                }`}
                onClick={() => setInputMode('docx')}
              >
                <Upload size={12} className="inline mr-1" /> DOCX 上传
              </button>
            </div>
          </div>
        </CardHeader>
        <CardBody className="space-y-4">
          {inputMode === 'text' ? (
            <Textarea
              label="待审内容"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="粘贴或输入待审改的中文内容..."
              rows={10}
              disabled={reviewing}
            />
          ) : (
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".docx"
                className="hidden"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
              <div
                className="border-2 border-dashed border-slate-200 rounded-lg p-8 text-center cursor-pointer hover:border-slate-400 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                {selectedFile ? (
                  <div className="flex items-center justify-center gap-2 text-sm text-slate-700">
                    <FileText size={20} className="text-blue-500" />
                    <span className="font-medium">{selectedFile.name}</span>
                    <span className="text-slate-400">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                  </div>
                ) : (
                  <div className="text-slate-400">
                    <Upload size={32} className="mx-auto mb-2" />
                    <p className="text-sm">点击选择 DOCX 文件</p>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="目标受众（可选）"
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
              placeholder="例如: 肿瘤科医生"
              disabled={reviewing}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">规则模式</label>
              <div className="flex rounded-md overflow-hidden border border-slate-200">
                <button
                  className={`flex-1 px-3 py-2 text-xs font-medium transition-colors ${
                    ruleMode === 'default' ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                  onClick={() => setRuleMode('default')}
                >
                  系统默认规则
                </button>
                <button
                  className={`flex-1 px-3 py-2 text-xs font-medium transition-colors ${
                    ruleMode === 'custom' ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                  onClick={() => setRuleMode('custom')}
                >
                  自定义规则
                </button>
              </div>
            </div>
          </div>

          {ruleMode === 'custom' && (
            <Textarea
              label="自定义规则（每行一条）"
              value={customRules}
              onChange={(e) => setCustomRules(e.target.value)}
              placeholder="输入自定义审改规则，每行一条..."
              rows={4}
              disabled={reviewing}
            />
          )}
        </CardBody>
        <CardFooter className="flex justify-end">
          <Button onClick={handleSubmit} disabled={!canSubmit || reviewing}>
            {reviewing ? <><Spinner size="sm" /> 审改中...</> : '开始审改'}
          </Button>
        </CardFooter>
      </Card>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Summary */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between w-full">
                <h3 className="text-sm font-semibold text-slate-800">审改结果</h3>
                <Badge variant={result.passed ? 'success' : 'danger'}>
                  {result.passed ? '通过' : '待改'}
                </Badge>
              </div>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div className="py-2">
                  <p className="text-lg font-bold text-blue-600">{result.severity_summary.low}</p>
                  <p className="text-xs text-slate-500">建议</p>
                </div>
                <div className="py-2">
                  <p className="text-lg font-bold text-amber-600">{result.severity_summary.medium}</p>
                  <p className="text-xs text-slate-500">中等</p>
                </div>
                <div className="py-2">
                  <p className="text-lg font-bold text-orange-600">{result.severity_summary.high}</p>
                  <p className="text-xs text-slate-500">严重</p>
                </div>
                <div className="py-2">
                  <p className="text-lg font-bold text-red-600">{result.severity_summary.critical}</p>
                  <p className="text-xs text-slate-500">致命</p>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Findings */}
          {result.findings.length > 0 && (
            <Card>
              <CardHeader>
                <h3 className="text-sm font-semibold text-slate-800">
                  审改发现 ({result.findings.length})
                </h3>
              </CardHeader>
              <CardBody className="p-0 divide-y divide-slate-100">
                {result.findings.map((f: ReviewFinding, i: number) => {
                  const cfg = SEVERITY_CONFIG[f.severity] || SEVERITY_CONFIG.low;
                  const Icon = cfg.icon;
                  return (
                    <div key={i} className="px-5 py-3">
                      <div className="flex items-start gap-3">
                        <Icon size={16} className={`${cfg.color} mt-0.5 flex-shrink-0`} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="default" size="sm">{f.category}</Badge>
                            <Badge variant="default" size="sm">{cfg.label}</Badge>
                          </div>
                          <p className="text-sm text-slate-700">{f.description}</p>
                          {f.location && <p className="text-xs text-slate-400 mt-1">位置: {f.location}</p>}
                          {f.suggestion && (
                            <p className="text-xs text-emerald-600 mt-1 bg-emerald-50 px-2 py-1 rounded">
                              建议: {f.suggestion}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </CardBody>
            </Card>
          )}

          {/* Rewrite Targets */}
          {result.rewrite_targets.length > 0 && (
            <Card>
              <CardHeader>
                <h3 className="text-sm font-semibold text-slate-800">
                  改写建议 ({result.rewrite_targets.length})
                </h3>
              </CardHeader>
              <CardBody className="p-0 divide-y divide-slate-100">
                {result.rewrite_targets.map((rt: ReviewRewriteTarget, i: number) => (
                  <div key={i} className="px-5 py-3 space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="warning" size="sm">优先级: {rt.priority}</Badge>
                      <span className="text-xs text-slate-500">{rt.reason}</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="bg-red-50 rounded p-2">
                        <p className="text-xs text-red-500 mb-1">原文</p>
                        <p className="text-sm text-slate-700">{rt.original}</p>
                      </div>
                      <div className="bg-emerald-50 rounded p-2">
                        <p className="text-xs text-emerald-500 mb-1">建议</p>
                        <p className="text-sm text-slate-700">{rt.suggested}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </CardBody>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
