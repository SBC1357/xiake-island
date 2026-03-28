"""
Contract 注册表

提供统一的 contract 模型注册和查询能力。
"""
from typing import Dict, Type, Optional
from pydantic import BaseModel


class ContractRegistry:
    """
    Contract 注册表
    
    职责:
        - 管理模块输入输出 schema
        - 管理 handoff 结构
        - 管理 contract 版本
        - 为测试和校验提供统一真相源
    """
    
    def __init__(self):
        self._contracts: Dict[str, Type[BaseModel]] = {}
        self._versions: Dict[str, str] = {}
    
    def register(
        self, 
        name: str, 
        model: Type[BaseModel], 
        version: str = "1.0.0"
    ) -> None:
        """
        注册一个 contract
        
        Args:
            name: contract 名称
            model: Pydantic 模型类
            version: contract 版本号
        """
        self._contracts[name] = model
        self._versions[name] = version
    
    def get(self, name: str) -> Optional[Type[BaseModel]]:
        """
        按名称获取 contract 模型
        
        Args:
            name: contract 名称
            
        Returns:
            Pydantic 模型类，不存在则返回 None
        """
        return self._contracts.get(name)
    
    def get_version(self, name: str) -> Optional[str]:
        """
        获取 contract 版本号
        
        Args:
            name: contract 名称
            
        Returns:
            版本号字符串，不存在则返回 None
        """
        return self._versions.get(name)
    
    def list_contracts(self) -> list[str]:
        """
        列出所有已注册的 contract 名称
        
        Returns:
            contract 名称列表
        """
        return list(self._contracts.keys())
    
    def is_registered(self, name: str) -> bool:
        """
        检查 contract 是否已注册
        
        Args:
            name: contract 名称
            
        Returns:
            是否已注册
        """
        return name in self._contracts


# 全局注册表实例
registry = ContractRegistry()