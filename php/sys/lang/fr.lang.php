<?php
	// FRENCH FILE LANG
	if(!isset($cfg) || !is_array($cfg)) die("");
	function translateDate($txt){
		$txt = str_replace("Monday","Lundi",
			str_replace("Tuesday","Mardi",
				str_replace("Wednesday","Mercredi",
					str_replace("Thursday","Jeudi",
						str_replace("Friday","Vendredi",
							str_replace("Saturday","Samedi",
								str_replace("Sunday","Dimanche",
									$txt
								)
							)
						)
					)
				)
			)
		);
		$txt = str_replace("January","Janvier",
			str_replace("February","Février",
				str_replace("March","Mars",
					str_replace("April","Avril",
						str_replace("May","Mai",
							str_replace("June","Juin",
								str_replace("July","Juillet",
									str_replace("August","Août",
										str_replace("September","Septembre",
											str_replace("October","Octobre",
												str_replace("November","Novembre",
													str_replace("December","Décembre",
														$txt
													)
												)
											)
										)
									)
								)
							)
						)
					)
				)
			)
		);
		return $txt;
	}	
	function translateText($txt){
		switch($txt){
			case 'NODATA':
				return "Pas de donnée trouvé.";
			break;
			case 'NOMAIL':
				return "Pas de nouveau courriel.";
			break;
			case 'NEWMAIL':
				return "nouveau courriel";
			break;
			case 'NEWMAILS':
				return "nouveaux courriels";
			break;
			case 'MAIL':
				return "courriel";
			break;
			case 'MAILS':
				return "courriels";
			break;
			case 'TODAY':
				return "Aujourd'hui";
			break;
			case 'FORECAST':
				return "Prévisions";
			break;
			case 'POWEROFF':
				return "Fermeture du Deskboard, aurevoir!";
			break;
			case 'REBOOT':
				return "Re-démarrage du Deskboard, à tantôt!";
			break;
			case 'TIME_MIDNIGHT':
				return "Il est actuellement minuit.";
			break;
			case 'TIME_ONEHOUR':
				return "Il est actuellement une heure.";
			break;
			case 'TIME_DINER':
				return "Il est actuellement midi.";
			break;
			case 'TIME_CURRENT':
				return "Il est actuellement %HOUR% heures.";
			break;
			case 'MAIL_YOUHAVEXNEW':
				return "Vous avez %UNREAD% nouveaux courriels.";
			break;
			case 'TIME_YOUARENOW':
				return "Nous sommes rendu le";
			break;
			case 'MAIL_ERRORGET':
				return "Impossible de consulter la boite de courriel.";
			break;
			case 'MAIL_NOMAIL':
				return "Vous avez aucun nouveau message.";
			break;
			case 'WEATHER_FORECAST_FOR':
				return "Prévisions météo pour ";
			break;
			case 'ERROR_MODULE_DISABLED':
				return "Le module est désactivé ou non configuré.";
			break;
			case 'ERROR_MODULE_NOTVALID':
				return "Le module n'existe pas ou n'est plus configuré.";
			break;
			case 'CTRL_TITLE':
				return "Gestion du dashboard";
			break;
			case 'CTRL_POWEROFF':
				return "Fermer le système";
			break;
			case 'CTRL_REBOOT':
				return "Redémarrer le système";
			break;
			case 'CTRL_REFRESH':
				return "Rafraîchir l'interface";
			break;
			case 'CTRL_BLUETOOTH':
				return "(Re)Connection au Bluetooth";
			break;
			case 'NOTHING':
				return "Rien";
			break;
			default:
				return "";
		}
	}	