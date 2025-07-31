import { createRouter, createWebHistory } from 'vue-router'
import PredictView from '../views/PredictView.vue'
import TrainView from '../views/TrainView.vue'

const routes = [
	{
		path: '/',
		name: 'predict',
		component: PredictView
	},
	{
		path: '/train',
		name: 'train',
		component: TrainView
	},
	{
		path: '/:catchAll(.*)',
		redirect: '/'
	}
];

const router = createRouter({
	history: createWebHistory(process.env.BASE_URL),
	routes
});

export default router;