# ClashRoyaleClanManager

A short script that computes statistics based on Clan Wars II weekly performance for a clan in Clash Royale.

requires:
1. the clan's tag (starting with #). Can be found (for example) here: https://royaleapi.com/?lang=en 
2. a token from supercell's API for Clash Royale: https://developer.clashroyale.com/#/
   the token can be associated with a number of IPs

Computes:
1. average war rank
2. weekly war champ (member with the most fame in the past war)

3. promotion/demotion/warning/kick lists to which members are added with the following rules:
    - promotion rule: two consecutive weeks of at least 1600 fame in war
    - demotion rule (elders): less than 1600 for two consecutive weeks 
    - warning rule: less than losing all attacks in 3/4 days in the last war 
    - kick rule: total score for two consecutive weeks is less than 2800. The thresshold can be achieved by losing all attacks in 3/4 (1200) and 4/4 (1600) days.

Decisions on clan updates can be made according to the four lists. The script also prints a full war history for all members in the kick list.

Feel free to update the rules according to your preferences!
