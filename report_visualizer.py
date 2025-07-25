import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_bid_report_visual(results_df: pd.DataFrame, optimal_info: pd.Series, base_price: float) -> str:
    """
    단일 예정가격 분석 결과를 시각화하여 이미지 파일로 저장합니다.
    """
    print("분석 결과 시각화 보고서를 생성합니다...")
    fig, ax1 = plt.subplots(figsize=(12, 7))

    color = 'tab:blue'
    ax1.set_xlabel('입찰률 (기초금액 대비 비율)', fontsize=12)
    ax1.set_ylabel('예상 승률', color=color, fontsize=12)
    ax1.plot(results_df['입찰률'], results_df['승률'], color=color, label='예상 승률', lw=2)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, axis='y', linestyle=':')

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('기대 수익 (원)', color=color, fontsize=12)
    ax2.plot(results_df['입찰률'], results_df['기대수익'], color=color, label='기대 수익', lw=2)
    ax2.tick_params(axis='y', labelcolor=color)

    optimal_rate = optimal_info['입찰률']
    plt.axvline(x=optimal_rate, color='green', linestyle='--', lw=2, label=f"수익 극대화 지점 ({optimal_rate:.2%})")
    plt.title(f'기초금액 {base_price:,.0f}원 최적 입찰 전략 분석', fontsize=16, pad=20)
    
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    fig.tight_layout()
    
    img_path = 'optimal_bid_report.png'
    plt.savefig(img_path)
    plt.close(fig)
    
    print(f"분석 보고서 그래프가 '{img_path}' 파일로 저장되었습니다.")
    return img_path
