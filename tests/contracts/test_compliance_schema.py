"""
SP-4 Compliance Checker Test
验证 ComplianceChecker.check() 返回结果对象而不是 import 失败
"""
import pytest


def test_compliance_checker_check_returns_result():
    """测试 ComplianceChecker.check() 返回结果对象"""
    from src.contracts.m5_compliance_schema import ComplianceChecker, ComplianceResult
    
    checker = ComplianceChecker()
    
    # 正常内容 - 应该通过
    result = checker.check("这是一段正常内容，不包含任何违规词语。")
    
    # 验证返回的是 ComplianceResult 对象
    assert isinstance(result, ComplianceResult)
    assert result.passed is True
    assert len(result.violations) == 0


def test_compliance_checker_detects_violation():
    """测试 ComplianceChecker 检测到违规"""
    from src.contracts.m5_compliance_schema import ComplianceChecker
    
    checker = ComplianceChecker()
    
    # 包含绝对化疗效宣称的内容
    result = checker.check("这个药物可以根治疾病，百分之百有效！")
    
    assert result.passed is False
    assert len(result.violations) > 0
    assert result.has_critical_violations is True


def test_compliance_checker_warning():
    """测试 ComplianceChecker 检测到警告"""
    from src.contracts.m5_compliance_schema import ComplianceChecker
    
    checker = ComplianceChecker()
    
    # 包含警告级别违规的内容
    result = checker.check("这是最新发现的突破性进展！")
    
    assert len(result.warnings) > 0