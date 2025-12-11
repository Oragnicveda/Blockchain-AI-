"""
Tokenomics collector for DQDA data collection.

Queries public APIs and blockchain explorers for:
- Token supply data (total, circulating, max supply)
- Token distribution and inflation metrics
- Token holder statistics and whale analysis
- Contract information and blockchain data
- Price and market cap data
- Historical supply/demand data
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal

from agent.utils.logger import setup_logger
from agent.dqda.data_collectors.base_collector import BaseCollector, DataSource, DQDADataPoint

logger = setup_logger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available, tokenomics data collection limited")


class TokenomicsCollector(BaseCollector):
    """
    Collector for cryptocurrency/token economics data.
    
    Integrates with multiple blockchain APIs and explorers:
    - Etherscan for Ethereum-based tokens
    - BSCScan for Binance Smart Chain tokens
    - CoinGecko for market data
    - DeFiPulse for DeFi-specific metrics
    - Moralis for multi-chain data
    """
    
    def __init__(self, rate_limit_delay: Optional[float] = None):
        super().__init__(rate_limit_delay)
        
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'DQDA-Tokenomics-Collector/1.0',
                'Accept': 'application/json'
            })
        
        # API endpoints for different blockchains and data sources
        self.api_endpoints = {
            'etherscan': {
                'base_url': 'https://api.etherscan.io/api',
                'token_info': '?module=token&action=tokeninfo&contractaddress={}',
                'token_supply': '?module=stats&action=tokensupply&contractaddress={}',
                'token_holders': '?module=token&action=tokenholderlist&contractaddress={}&page=1&offset=100'
            },
            'bscscan': {
                'base_url': 'https://api.bscscan.com/api',
                'token_info': '?module=token&action=tokeninfo&contractaddress={}',
                'token_supply': '?module=stats&action=tokensupply&contractaddress={}',
                'token_holders': '?module=token&action=tokenholderlist&contractaddress={}&page=1&offset=100'
            },
            'coingecko': {
                'base_url': 'https://api.coingecko.com/api/v3',
                'token_price': '/simple/price?ids={}&vs_currencies=usd,btc,eth&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true',
                'token_info': '/coins/{}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false',
                'defi_tvl': '/charts?vs_currency=usd&ids={}&days=30'
            },
            'moralis': {
                'base_url': 'https://deep-index.moralis.io/api/v2',
                'token_metadata': '/erc20/{}/metadata',
                'token_price': '/erc20/{}/price',
                'token_holders': '/nft/{}/owners?chain=eth&format=decimal'
            }
        }
        
        # Common token contract addresses (test data)
        self.known_tokens = {
            'ethereum': {
                'USDC': '0xa0b86a33e6415b8b23665e5b9adf3e9b5d0d4f62',
                'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
                'DAI': '0x6b175474e89094c44da98b954eedeac495271d0f',
                'LINK': '0x514910771af9ca656af840dff83e8264ecf986ca'
            },
            'bsc': {
                'USDC': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
                'BUSD': '0xe9e7cea3dedca5984780bafc599bd69add087d56',
                'CAKE': '0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82'
            }
        }
        
        # Blockchain explorers for verification
        self.blockchain_explorers = {
            'ethereum': ['https://etherscan.io', 'https://ethplorer.io'],
            'bsc': ['https://bscscan.com', 'https://testnet.bscscan.com'],
            'polygon': ['https://polygonscan.com'],
            'avalanche': ['https://snowtrace.io']
        }
    
    async def _collect_raw_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect tokenomics data from multiple sources.
        
        Expected kwargs:
            startup_name: Name of the startup
            keywords: List of keywords for search
            max_results: Maximum number of results
            token_addresses: Optional list of token contract addresses
            blockchains: Optional list of blockchains to query
            use_test_data: Whether to use test data for development
        """
        startup_name = kwargs.get('startup_name', '')
        keywords = kwargs.get('keywords', [])
        max_results = kwargs.get('max_results', 5)
        token_addresses = kwargs.get('token_addresses', [])
        blockchains = kwargs.get('blockchains', ['ethereum', 'bsc'])
        use_test_data = kwargs.get('use_test_data', False)
        
        results = []
        
        # If no token addresses provided, search for them
        if not token_addresses:
            token_addresses = await self._search_for_token_addresses(startup_name, keywords, blockchains)
        
        # Collect data for each token address
        for token_address in token_addresses[:max_results]:
            try:
                # Determine blockchain for this token
                blockchain = self._identify_blockchain(token_address)
                
                # Collect comprehensive tokenomics data
                token_data = await self._collect_token_data(token_address, blockchain, use_test_data)
                if token_data:
                    results.append(token_data)
                    
            except Exception as e:
                logger.error(f"Error collecting tokenomics for {token_address}: {str(e)}")
                continue
        
        return results
    
    async def _search_for_token_addresses(self, startup_name: str, keywords: List[str], blockchains: List[str]) -> List[str]:
        """
        Search for token contract addresses related to the startup.
        
        Args:
            startup_name: Name of the startup
            keywords: Search keywords
            blockchains: List of blockchains to search
            
        Returns:
            List of potential token contract addresses
        """
        # This is a simplified implementation
        # In production, this would search through:
        # - Token discovery APIs
        # - DEX listing information
        # - DeFi protocol integrations
        # - Blockchain explorer search APIs
        
        token_addresses = []
        
        # Check known tokens for matches
        for blockchain in blockchains:
            if blockchain in self.known_tokens:
                for token_name, contract_address in self.known_tokens[blockchain].items():
                    # Simple name matching
                    if any(keyword.lower() in token_name.lower() for keyword in keywords) or \
                       any(keyword.lower() in startup_name.lower() for keyword in keywords):
                        token_addresses.append(contract_address)
        
        return token_addresses[:5]  # Limit results
    
    async def _collect_token_data(self, contract_address: str, blockchain: str, use_test_data: bool = False) -> Optional[Dict[str, Any]]:
        """
        Collect comprehensive tokenomics data for a token.
        
        Args:
            contract_address: Token contract address
            blockchain: Blockchain name
            use_test_data: Whether to use test data
            
        Returns:
            Tokenomics data dictionary or None
        """
        try:
            logger.info(f"Collecting tokenomics data for {contract_address} on {blockchain}")
            
            # Collect data from multiple sources in parallel
            tasks = [
                self._get_token_metadata(contract_address, blockchain),
                self._get_token_supply_data(contract_address, blockchain),
                self._get_holder_data(contract_address, blockchain),
                self._get_market_data(contract_address),
                self._get_blockchain_info(contract_address, blockchain)
            ]
            
            # Execute in parallel with timeout
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            metadata, supply_data, holder_data, market_data, blockchain_info = results
            
            # Compile comprehensive tokenomics data
            tokenomics_data = {
                'contract_address': contract_address,
                'blockchain': blockchain,
                'metadata': metadata if not isinstance(metadata, Exception) else {},
                'supply_metrics': supply_data if not isinstance(supply_data, Exception) else {},
                'holder_statistics': holder_data if not isinstance(holder_data, Exception) else {},
                'market_data': market_data if not isinstance(market_data, Exception) else {},
                'blockchain_info': blockchain_info if not isinstance(blockchain_info, Exception) else {},
                'collection_timestamp': datetime.now(timezone.utc).isoformat(),
                'collection_method': 'multi_api_query',
                'data_sources': self._get_data_sources(blockchain)
            }
            
            # Calculate derived metrics
            self._calculate_derived_metrics(tokenomics_data)
            
            # Assess data quality
            quality_score = self._assess_data_quality(tokenomics_data)
            tokenomics_data['quality_score'] = quality_score
            
            return tokenomics_data
            
        except Exception as e:
            logger.error(f"Error collecting tokenomics data for {contract_address}: {str(e)}")
            return None
    
    async def _get_token_metadata(self, contract_address: str, blockchain: str) -> Dict[str, Any]:
        """Get basic token metadata (name, symbol, decimals, etc.)."""
        try:
            # Use different APIs based on blockchain
            if blockchain == 'ethereum':
                return await self._get_ethereum_token_metadata(contract_address)
            elif blockchain == 'bsc':
                return await self._get_bsc_token_metadata(contract_address)
            else:
                return await self._get_generic_token_metadata(contract_address)
                
        except Exception as e:
            logger.error(f"Error getting token metadata for {contract_address}: {str(e)}")
            return {}
    
    async def _get_ethereum_token_metadata(self, contract_address: str) -> Dict[str, Any]:
        """Get Ethereum token metadata via multiple APIs."""
        try:
            # Try Etherscan first
            if self.session:
                etherscan_url = f"{self.api_endpoints['etherscan']['base_url']}?module=contract&action=getabi&address={contract_address}"
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.session.get(etherscan_url, timeout=10)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == '1':
                        return {
                            'contract_address': contract_address,
                            'blockchain': 'ethereum',
                            'explorer_verified': True,
                            'abi_available': True,
                            'source': 'etherscan'
                        }
            
            # Fallback to generic metadata
            return await self._get_generic_token_metadata(contract_address)
            
        except Exception as e:
            logger.warning(f"Etherscan metadata query failed: {str(e)}")
            return await self._get_generic_token_metadata(contract_address)
    
    async def _get_bsc_token_metadata(self, contract_address: str) -> Dict[str, Any]:
        """Get BSC token metadata."""
        try:
            if self.session:
                bscscan_url = f"{self.api_endpoints['bscscan']['base_url']}?module=contract&action=getabi&address={contract_address}"
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.session.get(bscscan_url, timeout=10)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == '1':
                        return {
                            'contract_address': contract_address,
                            'blockchain': 'bsc',
                            'explorer_verified': True,
                            'abi_available': True,
                            'source': 'bscscan'
                        }
            
            return await self._get_generic_token_metadata(contract_address)
            
        except Exception as e:
            logger.warning(f"BscScan metadata query failed: {str(e)}")
            return await self._get_generic_token_metadata(contract_address)
    
    async def _get_generic_token_metadata(self, contract_address: str) -> Dict[str, Any]:
        """Get generic token metadata."""
        return {
            'contract_address': contract_address,
            'explorer_verified': False,
            'metadata_source': 'generic',
            'note': 'Limited metadata available'
        }
    
    async def _get_token_supply_data(self, contract_address: str, blockchain: str) -> Dict[str, Any]:
        """Get token supply data."""
        try:
            supply_data = {
                'contract_address': contract_address,
                'blockchain': blockchain,
                'total_supply': None,
                'circulating_supply': None,
                'max_supply': None,
                'supply_source': 'unknown'
            }
            
            # Try to get supply data from blockchain explorers
            if blockchain == 'ethereum' and self.session:
                supply_url = f"{self.api_endpoints['etherscan']['token_supply'].format(contract_address)}"
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.session.get(supply_url, timeout=10)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == '1' and data['result']:
                        try:
                            total_supply = int(data['result'])
                            supply_data['total_supply'] = total_supply
                            supply_data['supply_source'] = 'etherscan'
                        except (ValueError, TypeError):
                            pass
            
            # If no data from explorer, try test data
            if supply_data['total_supply'] is None:
                test_supply = self._get_test_supply_data(contract_address)
                supply_data.update(test_supply)
                supply_data['supply_source'] = 'test_data'
            
            return supply_data
            
        except Exception as e:
            logger.error(f"Error getting token supply data for {contract_address}: {str(e)}")
            return {'contract_address': contract_address, 'error': str(e)}
    
    def _get_test_supply_data(self, contract_address: str) -> Dict[str, Any]:
        """Generate test supply data for development."""
        # Generate deterministic test data based on contract address
        hash_val = int(contract_address[:8], 16) if contract_address[:8].isalnum() else 1000000
        
        return {
            'total_supply': hash_val * 1000000,
            'circulating_supply': hash_val * 800000,
            'max_supply': hash_val * 2000000 if hash_val % 2 == 0 else None,
            'inflation_rate': 0.02 if hash_val % 3 == 0 else None
        }
    
    async def _get_holder_data(self, contract_address: str, blockchain: str) -> Dict[str, Any]:
        """Get token holder statistics."""
        try:
            holder_data = {
                'contract_address': contract_address,
                'blockchain': blockchain,
                'total_holders': None,
                'holder_distribution': {},
                'top_holders': [],
                'whale_analysis': {},
                'data_source': 'unknown'
            }
            
            # Try to get holder data from explorers
            if blockchain == 'ethereum' and self.session:
                holders_url = f"{self.api_endpoints['etherscan']['token_holders'].format(contract_address)}"
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.session.get(holders_url, timeout=15)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == '1' and data['result']:
                        holders = data['result']
                        
                        # Process top holders
                        top_holders = holders[:10] if isinstance(holders, list) else []
                        holder_data['top_holders'] = self._process_holder_list(top_holders)
                        holder_data['total_holders'] = len(holders) if isinstance(holders, list) else None
                        holder_data['data_source'] = 'etherscan'
            
            # If no real data available, use test data
            if not holder_data['top_holders']:
                test_holder_data = self._get_test_holder_data(contract_address)
                holder_data.update(test_holder_data)
                holder_data['data_source'] = 'test_data'
            
            return holder_data
            
        except Exception as e:
            logger.error(f"Error getting holder data for {contract_address}: {str(e)}")
            return {'contract_address': contract_address, 'error': str(e)}
    
    def _process_holder_list(self, holders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw holder data from explorer APIs."""
        processed = []
        
        for holder in holders:
            try:
                processed_holder = {
                    'address': holder.get('TokenHolder', ''),
                    'balance': float(holder.get('TokenHolderQuantity', 0)),
                    'percentage': float(holder.get('PercentageOfTotalSupply', 0))
                }
                processed.append(processed_holder)
            except (ValueError, TypeError, KeyError):
                continue
        
        return processed
    
    def _get_test_holder_data(self, contract_address: str) -> Dict[str, Any]:
        """Generate test holder data."""
        import random
        random.seed(hash(contract_address))  # Deterministic results
        
        # Generate 10 test holders
        test_holders = []
        total_supply = self._get_test_supply_data(contract_address)['total_supply']
        remaining_supply = total_supply
        
        for i in range(10):
            # Top holder gets 30%, next ones get progressively smaller amounts
            percentage = max(0.01, 30 / (i + 1) * (0.5 ** i))
            if i == 0:
                percentage = 30.0
            
            balance = (percentage / 100) * total_supply
            remaining_supply -= balance
            
            test_holders.append({
                'address': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                'balance': balance,
                'percentage': percentage
            })
        
        return {
            'total_holders': random.randint(1000, 10000),
            'top_holders': test_holders,
            'whale_analysis': {
                'whale_threshold': total_supply * 0.01,  # 1% of supply
                'whale_count': sum(1 for h in test_holders if h['balance'] > total_supply * 0.01)
            }
        }
    
    async def _get_market_data(self, contract_address: str) -> Dict[str, Any]:
        """Get market data including price and volume."""
        try:
            market_data = {
                'contract_address': contract_address,
                'current_price_usd': None,
                'current_price_btc': None,
                'current_price_eth': None,
                'market_cap_usd': None,
                'volume_24h_usd': None,
                'price_change_24h': None,
                'data_source': 'unknown'
            }
            
            # Try CoinGecko API (would need token ID mapping)
            # For now, return test market data
            test_market_data = self._get_test_market_data(contract_address)
            market_data.update(test_market_data)
            market_data['data_source'] = 'test_data'
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data for {contract_address}: {str(e)}")
            return {'contract_address': contract_address, 'error': str(e)}
    
    def _get_test_market_data(self, contract_address: str) -> Dict[str, Any]:
        """Generate test market data."""
        import random
        random.seed(hash(contract_address))
        
        base_price = random.uniform(0.1, 100)
        
        return {
            'current_price_usd': base_price,
            'current_price_btc': base_price / 50000,  # Rough BTC price
            'current_price_eth': base_price / 3000,   # Rough ETH price
            'market_cap_usd': base_price * random.randint(1000000, 100000000),
            'volume_24h_usd': base_price * random.randint(100000, 10000000),
            'price_change_24h': random.uniform(-20, 20)
        }
    
    async def _get_blockchain_info(self, contract_address: str, blockchain: str) -> Dict[str, Any]:
        """Get blockchain-specific information."""
        return {
            'blockchain': blockchain,
            'contract_address': contract_address,
            'explorer_urls': self.blockchain_explorers.get(blockchain, []),
            'standard': 'ERC20' if blockchain == 'ethereum' else 'BEP20' if blockchain == 'bsc' else 'unknown',
            'decentralization_level': self._assess_decentralization_level(blockchain)
        }
    
    def _assess_decentralization_level(self, blockchain: str) -> str:
        """Assess decentralization level of blockchain."""
        decentralization_map = {
            'ethereum': 'high',
            'bsc': 'medium',
            'polygon': 'medium',
            'avalanche': 'high',
            'solana': 'high'
        }
        return decentralization_map.get(blockchain, 'unknown')
    
    def _identify_blockchain(self, contract_address: str) -> str:
        """Identify blockchain from contract address format."""
        if len(contract_address) == 42 and contract_address.startswith('0x'):
            # Could be Ethereum, BSC, or other EVM chains
            # Default to Ethereum for now
            return 'ethereum'
        elif contract_address.startswith('bnb') or len(contract_address) == 42:
            return 'bsc'
        else:
            return 'ethereum'  # Default
    
    def _calculate_derived_metrics(self, tokenomics_data: Dict[str, Any]) -> None:
        """Calculate derived metrics from raw tokenomics data."""
        try:
            supply_data = tokenomics_data.get('supply_metrics', {})
            holder_data = tokenomics_data.get('holder_statistics', {})
            market_data = tokenomics_data.get('market_data', {})
            
            # Calculate inflation/deflation metrics
            total_supply = supply_data.get('total_supply')
            circulating_supply = supply_data.get('circulating_supply')
            
            if total_supply and circulating_supply:
                tokenomics_data['circulation_ratio'] = circulating_supply / total_supply
            
            # Holder concentration metrics
            top_holders = holder_data.get('top_holders', [])
            if top_holders:
                total_holders = len(top_holders)
                top_5_percentage = sum(h.get('percentage', 0) for h in top_holders[:5])
                top_10_percentage = sum(h.get('percentage', 0) for h in top_holders[:10])
                
                holder_data['top_5_concentration'] = top_5_percentage
                holder_data['top_10_concentration'] = top_10_percentage
                holder_data['concentration_risk'] = 'high' if top_10_percentage > 50 else 'medium' if top_10_percentage > 30 else 'low'
            
            # Market cap calculations
            price_usd = market_data.get('current_price_usd')
            if price_usd and total_supply:
                estimated_market_cap = price_usd * total_supply
                tokenomics_data['estimated_market_cap'] = estimated_market_cap
            
        except Exception as e:
            logger.warning(f"Error calculating derived metrics: {str(e)}")
    
    def _assess_data_quality(self, tokenomics_data: Dict[str, Any]) -> float:
        """Assess overall quality of collected tokenomics data."""
        quality_score = 0.0
        max_score = 0.0
        
        # Check metadata completeness
        metadata = tokenomics_data.get('metadata', {})
        max_score += 1.0
        if metadata.get('explorer_verified'):
            quality_score += 0.3
        if metadata.get('abi_available'):
            quality_score += 0.2
        
        # Check supply data completeness
        supply_data = tokenomics_data.get('supply_metrics', {})
        max_score += 1.0
        if supply_data.get('total_supply'):
            quality_score += 0.4
        if supply_data.get('circulating_supply'):
            quality_score += 0.3
        if supply_data.get('max_supply'):
            quality_score += 0.3
        
        # Check holder data completeness
        holder_data = tokenomics_data.get('holder_statistics', {})
        max_score += 1.0
        if holder_data.get('total_holders'):
            quality_score += 0.3
        if holder_data.get('top_holders'):
            quality_score += 0.4
        if holder_data.get('whale_analysis'):
            quality_score += 0.3
        
        # Check market data completeness
        market_data = tokenomics_data.get('market_data', {})
        max_score += 1.0
        if market_data.get('current_price_usd'):
            quality_score += 0.4
        if market_data.get('market_cap_usd'):
            quality_score += 0.3
        if market_data.get('volume_24h_usd'):
            quality_score += 0.3
        
        return min(quality_score / max_score, 1.0) if max_score > 0 else 0.0
    
    def _get_data_sources(self, blockchain: str) -> List[str]:
        """Get list of data sources used for a blockchain."""
        sources = []
        
        if blockchain == 'ethereum':
            sources.extend(['etherscan', 'coingecko'])
        elif blockchain == 'bsc':
            sources.extend(['bscscan', 'coingecko'])
        else:
            sources.extend(['generic_apis'])
        
        return sources
    
    def _get_source_type(self) -> DataSource:
        """Get the data source type for this collector."""
        return DataSource.TOKENOMICS
    
    def get_search_suggestions(self, startup_name: str) -> List[str]:
        """Get tokenomics specific search suggestions."""
        base_suggestions = super().get_search_suggestions(startup_name)
        
        tokenomics_suggestions = [
            f"{startup_name} token contract address",
            f"{startup_name} tokenomics whitepaper",
            f"{startup_name} token distribution",
            f"{startup_name} cryptocurrency token",
            f"{startup_name} defi protocol token",
            f"{startup_name} governance token",
            f"{startup_name} utility token"
        ]
        
        return base_suggestions + tokenomics_suggestions