"use client"

import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import {
	Chart as ChartJS,
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Title,
	Tooltip,
	Legend,
} from 'chart.js'
import { getEarningsData } from '@/lib/api'

ChartJS.register(
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Title,
	Tooltip,
	Legend
)

interface EarningsData {
	date: string
	amount: number
}

export function EarningsChart() {
	const [earningsData, setEarningsData] = useState<EarningsData[]>([])

	useEffect(() => {
		const fetchEarnings = async () => {
			try {
				const data = await getEarningsData();
				setEarningsData(data);
			} catch (error) {
				console.error('Error fetching earnings data:', error);
			}
		};

		fetchEarnings();
	}, []);

	const chartData = {
		labels: earningsData.map(d => d.date),
		datasets: [
			{
				label: 'Earnings',
				data: earningsData.map(d => d.amount),
				borderColor: 'rgb(75, 192, 192)',
				tension: 0.1
			}
		]
	};

	const options = {
		responsive: true,
		plugins: {
			legend: {
				position: 'top' as const,
			},
			title: {
				display: true,
				text: 'Earnings Over Time'
			}
		}
	};

	return <Line options={options} data={chartData} />;
}