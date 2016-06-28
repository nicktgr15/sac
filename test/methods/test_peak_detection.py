from unittest import TestCase

import peakutils
from sac.methods import peak_detection
import matplotlib.pyplot as plt


class TestPeakDetection(TestCase):

    def test_find_peaks(self):

        series_data = [-24.042454961429666, -18.0993048923164, -13.828318484140262, -10.569212093730812, -7.4060114865180111, -5.1350226377188495, -3.3370182551906802, -0.89380139887591081, 2.369241136723252, 5.2196346943553484, 6.923593978090322, 4.5677419547153004, 2.1735348926462605, 1.8400498222230732, 3.5195594252556361, 7.1959770412734834, 15.955955076446202, 33.458606045285748, 59.686359023760104, 91.543148545931473, 123.54444836501366, 141.67641328999952, 139.55037256151778, 122.86008300283368, 93.732766654324308, 61.108133413233503, 32.8479833293935, 13.302124877005078, 4.5958305241394459, 3.221119370652469, 6.2974996256215334, 10.71034236242275, 12.621161632778907, 10.970715287162017, 6.8784893179453732, 6.3386299866448201, 14.03100335361918, 33.439065061951567, 58.857580467322073, 82.064215315532238, 99.530176951724144, 104.35355576270334, 92.441757181504414, 72.302678621485171, 53.645169739528683, 40.163430997797164, 28.598645946285156, 18.168172839120899, 10.085650087467362, 4.7096410357183469, 1.7706961276806585, 0.98146397262248619, 0.98484100414113041, 0.98926001081169523, 1.6080005985639358, 3.1471956749097423, 5.6334436754552888, 9.6347170256211889, 15.492156845801665, 22.250800699967971, 29.531342476267191, 35.67343589403027, 38.395464210515399, 37.20315236867728, 32.463052295635975, 25.755426052639571, 18.56606550086601, 12.195226864374412, 7.5081736402471417, 4.2839998661202925, 2.0667755881056888, 0.85586169117217858, 0.61879567152042059, 1.3488712355492605, 2.8628319246122591, 5.1284144082202543, 8.1690099237185887, 11.362878946311234, 14.198985754728085, 17.089774089699482, 19.97251192419612, 20.672087874198496, 17.471379256214217, 13.147824792181591, 9.625062399830405, 6.428894361566531, 3.1148107014263497, 0.69854350550664712, 0.35067437006370561, 1.9180749727844884, 4.9491003158536344, 8.2623904128602632, 10.840473309607676, 15.549777428581917, 24.08797774270532, 35.538010149500074, 46.192878294360497, 53.190008346634329, 61.802163230473099, 78.608506142101447, 103.15676087540163, 124.07324291864651, 125.1300245497776, 107.0691892779173, 84.163232822806123, 63.681737839073122, 46.756711279504145, 33.413515242029504, 22.151011406788484, 12.282373539429095, 5.2889778415238204, 2.1327968044929344, 2.3255273042229287, 4.7871721824221609, 8.2508504653562689, 12.755771780593594, 17.004314957504537, 19.686784763661208, 22.357326032184162, 28.140913315195107, 36.203910365645747, 40.493737357121418, 35.789694638598583, 24.200796316897787, 14.257290635191147, 8.9607865547109942, 6.3543869620258198, 4.8886827822767183, 3.8641231508535938, 3.7760106292117976, 5.464179621197955, 6.7647326524534819, 6.3004715391195489, 3.8653473751519218, 1.4413542983043541, 2.5817601259855243, 5.8426879820344757, 9.1272174419836745, 12.835474180738821, 19.304148376332716, 30.170083273436287, 44.663850562152575, 61.150455638405035, 69.349890059289635, 58.411527257381159, 42.008978716311475, 30.980211967311611, 24.45657886243038, 18.301507143710872, 10.057218769814156, 3.1337409797426132, 3.4368388655540105, 11.278457510013936, 18.863952127361934, 21.649726041477734, 25.961996143372676, 32.925901066162197, 38.825994762189858, 45.151359575665275, 56.52664493824188, 73.505289682398484, 98.157363444008752, 121.16667151589954, 122.4506288812579, 105.52971685701263, 85.481240526571753, 65.84014604974287, 44.436859537947804, 25.05618331539219, 12.985329326210181, 10.176180245075885, 13.815764985304487, 19.884812590190379, 26.494312979222308, 34.035126597205497, 40.903851933372984, 42.772825612607747, 42.780319905685744, 52.233683915042192, 73.014805218544097, 101.69319646710466, 128.63330870771401, 141.59714168792812, 134.81264063235776, 118.04689118536143, 100.258406194689, 80.006181893996029, 57.318124071623558]

        peaks = peak_detection.find_peaks(series_data)

        self.assertListEqual([21, 41, 62, 102, 121, 143, 163, 182], peaks)
        # peaks_peakutils = peakutils.indexes(series_data)
        # plt.figure()
        # plt.plot(series_data)
        # plt.plot(ranking, '-')
        # plt.plot(peaks, [series_data[p] for p in peaks], 'x')
        # plt.plot(peaks_peakutils, [series_data[p] + 2 for p in peaks_peakutils], '.')
        # plt.show()