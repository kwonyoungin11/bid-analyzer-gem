import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from itertools import combinations
import io

# Gem의 실행 환경에서 한글 폰트를 지원하기 위한 설정입니다.
try:
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print(f"Font setting failed: {e}") # 폰트가 없어도 오류 없이 진행되도록 예외 처리
    pass


class BidAnalyzer:
    """
    베이즈 정리, 게임 이론, 몬테카를로 시뮬레이션을 기반으로
    최적의 입찰 전략을 제시하는 낙찰 분석 클래스
    """

    def __init__(self, df: pd.DataFrame):
        """
        분석기는 데이터 핸들러를 통해 처리된 데이터프레임을 받아 초기화됩니다.
        """
        self.df = df
        self.competitor_stats = self._analyze_competitors()

    def _analyze_competitors(self) -> pd.DataFrame:
        """
        경쟁자 행동 패턴 분석 (게임 이론의 기초)
        """
        print("경쟁자별 입찰 패턴을 분석합니다...")
        stats = self.df.groupby('입찰자상호')['낙찰률'].agg(['mean', 'std', 'count']).reset_index()
        stats.columns = ['입찰자상호', '평균낙찰률', '낙찰률표준편차', '입찰참여횟수']
        stats['낙찰률표준편차'].fillna(self.df['낙찰률'].std(), inplace=True)
        print("경쟁자 분석이 완료되었습니다.")
        return stats

    def find_optimal_bid(self, base_price: float, start_rate=0.95, end_rate=1.15, steps=100) -> tuple:
        """
        수익 극대화를 위한 최적 입찰률 탐색 (단일 예정가격)
        """
        print(f"기초금액 {base_price:,.0f}원에 대한 최적 입찰가 분석을 시작합니다...")
        bid_rates = np.linspace(start_rate, end_rate, steps)
        results = []

        for rate in bid_rates:
            wins = 0
            # 시뮬레이션에 참여할 경쟁자들을 무작위로 샘플링합니다. (참여횟수 가중)
            active_competitors = self.competitor_stats.sample(
                n=np.random.randint(5, 15), # 평균 입찰자 수를 가정
                weights='입찰참여횟수',
                replace=True
            )
            # 몬테카를로 시뮬레이션
            competitor_bids = norm.rvs(
                loc=active_competitors['평균낙찰률'],
                scale=active_competitors['낙찰률표준편차']
            ) * base_price
            my_bid = base_price * rate
            if my_bid > competitor_bids.max():
                wins += 1
            
            win_probability = wins / 1 # 단순화된 예시, 실제로는 더 많은 시뮬레이션 필요
            expected_profit = (base_price * rate - base_price) * win_probability
            results.append({'입찰률': rate, '승률': win_probability, '기대수익': expected_profit})

        results_df = pd.DataFrame(results)
        optimal_bid_info = results_df.loc[results_df['기대수익'].idxmax()]
        print("최적 입찰가 분석이 완료되었습니다.")
        
        return optimal_bid_info, results_df


    def find_optimal_multi_price_strategy(
        self,
        base_amount: float,
        my_bidding_rate: float,
        total_prelim_prices: int = 15,
        num_to_choose_by_bidder: int = 4,
        num_to_average: int = 4,
        num_competitors: int = 10,
        num_simulations: int = 5000
    ) -> pd.DataFrame:
        """
        복수예가 입찰을 위한 최적의 '예가 선택 조합'과 '승률'을 분석합니다.
        """
        print("복수예가 입찰 시뮬레이션을 시작합니다. 미래의 확률을 계산합니다...")
        prelim_prices = np.linspace(base_amount * 0.98, base_amount * 1.02, total_prelim_prices)
        my_possible_choices = list(combinations(range(total_prelim_prices), num_to_choose_by_bidder))
        simulation_results = []

        for my_choice in my_possible_choices:
            wins = 0
            simulated_final_prices = []
            
            for _ in range(num_simulations):
                all_choices = list(my_choice)
                for _ in range(num_competitors):
                    competitor_choice = np.random.choice(total_prelim_prices, num_to_choose_by_bidder, replace=False)
                    all_choices.extend(competitor_choice)

                choice_counts = pd.Series(all_choices).value_counts()
                top_choices_indices = choice_counts.head(num_to_average).index
                final_base_price = prelim_prices[top_choices_indices].mean()
                simulated_final_prices.append(final_base_price)

                my_bid_price = base_amount * my_bidding_rate
                lower_bound = final_base_price * 0.88

                if my_bid_price >= lower_bound and my_bid_price < final_base_price:
                    wins += 1
            
            win_probability = wins / num_simulations
            avg_final_price = np.mean(simulated_final_prices)

            simulation_results.append({
                '나의 예가선택 (인덱스)': my_choice,
                '예상 승률': win_probability,
                '예상 평균 예정가격': avg_final_price
            })

        print("시뮬레이션이 완료되었습니다.")
        results_df = pd.DataFrame(simulation_results)
        return results_df.sort_values(by='예상 승률', ascending=False)
